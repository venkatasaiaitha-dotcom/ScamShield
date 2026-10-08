from typing import Dict, Any, List
from ..services.url_analyzer import URLAnalyzer
from ..services.message_analyzer import MessageAnalyzer
from ..services.risk_engine import RiskEngine
from ..services.explanation_engine import ExplanationEngine
from ..services.multilingual_engine import MultilingualEngine
from ..services.upi_guard import UPIGuard
from ..services.dna_engine import ScamDNAEngine
from ..services.attack_chain_service import AttackChainService
from ..database import record_or_update_campaign
from ..models.schemas import RiskLevel, ScamCategory, AnalysisReason

class HybridScamClassifier:
    """
    Hybrid Classification System (SOC-Enhanced):
    Combines rule-based contextual indicators, deep URL analysis,
    multilingual code-mix normalization, UPI payment safety guard,
    Scam DNA campaign fingerprinting, and attack chain stage correlation.
    """
    def __init__(self):
        self.url_analyzer = URLAnalyzer()
        self.message_analyzer = MessageAnalyzer()
        self.risk_engine = RiskEngine()
        self.explanation_engine = ExplanationEngine()

    def process(
        self,
        content: str,
        sender: str,
        custom_high_thresh: int = 70,
        custom_susp_thresh: int = 30
    ) -> Dict[str, Any]:
        # 1. Indian Multilingual & Code-Mixed Normalization
        multilingual_info = MultilingualEngine.analyze(content)

        # 2. Extract and analyze all URLs
        urls = self.url_analyzer.extract_urls(content)
        url_analyses = [self.url_analyzer.analyze_url(u) for u in urls]

        # 3. NLP & Context-aware message heuristic analysis
        raw_score, category, reasons, tech_signals = self.message_analyzer.analyze_text(
            content=content,
            sender=sender,
            urls=url_analyses
        )

        # If code-mixed signals detected, apply risk boost and add to reasons
        if multilingual_info.get("is_code_mixed") and multilingual_info.get("matched_signals"):
            raw_score += multilingual_info.get("risk_boost", 0)
            tech_signals["multilingual_signals"] = multilingual_info["matched_signals"]
            reasons.append(AnalysisReason(
                title=f"Code-Mixed Deception ({', '.join(multilingual_info['detected_languages'])})",
                description="Message incorporates Indian regional language colloquialisms to bypass standard keyword filters.",
                severity="HIGH" if multilingual_info["risk_boost"] >= 20 else "MEDIUM"
            ))

        # 4. UPI Payment Safety Guard Analysis
        claimed_brand = tech_signals.get("impersonation_target") or sender
        upi_analysis = UPIGuard.analyze(content, claimed_brand=claimed_brand)
        if upi_analysis.get("has_upi_payload"):
            tech_signals["upi_safety"] = upi_analysis
            if upi_analysis["safety_verdict"] == "HIGH_RISK_DO_NOT_PAY":
                raw_score += 35
                if category == ScamCategory.NORMAL:
                    category = ScamCategory.UPI_FRAUD
                for upi_reason in upi_analysis.get("reasons", []):
                    reasons.append(AnalysisReason(
                        title="UPI Payment Safety Flag",
                        description=upi_reason,
                        severity="HIGH"
                    ))
            elif upi_analysis["safety_verdict"] == "VERIFY_BEFORE_PAYING":
                raw_score += 15
                for upi_reason in upi_analysis.get("reasons", []):
                    reasons.append(AnalysisReason(
                        title="Unverified UPI Receiver Handle",
                        description=upi_reason,
                        severity="MEDIUM"
                    ))

        # 5. Transparent Risk Engine calculation
        final_score, risk_level = self.risk_engine.evaluate_risk(
            raw_score=raw_score,
            custom_high=custom_high_thresh,
            custom_suspicious=custom_susp_thresh
        )

        # 6. Generate Explainable Reasoning and Action Guidance
        summary, recommendations = self.explanation_engine.generate_explanation(
            risk_level=risk_level,
            category=category,
            reasons=reasons,
            urls=url_analyses,
            technical_signals=tech_signals
        )

        # Add UPI-specific advice if payment is involved
        if upi_analysis.get("has_upi_payload"):
            if upi_analysis["safety_verdict"] == "HIGH_RISK_DO_NOT_PAY":
                recommendations.donts.insert(0, f"DO NOT authorize UPI payment to {upi_analysis['primary_vpa']}")
                recommendations.dos.insert(0, "Never enter UPI PIN to 'receive' money or refunds. UPI PIN is solely for deducting funds.")

        # 7. Scam DNA & Campaign Fingerprinting
        dna_info = ScamDNAEngine.generate_fingerprint(
            content=content,
            sender=sender,
            category=category.value,
            urls=url_analyses,
            upi_data=upi_analysis if upi_analysis.get("has_upi_payload") else None,
            impersonation_target=tech_signals.get("impersonation_target")
        )

        # Record or match campaign in database for live variant & immunity tracking
        campaign_record = {}
        try:
            campaign_record = record_or_update_campaign(dna_info)
        except Exception:
            campaign_record = {
                "campaign_id": dna_info["campaign_id"],
                "dna_hash": dna_info["dna_hash"],
                "scam_type": dna_info["scam_type"],
                "impersonated_brand": dna_info["impersonated_brand"],
                "attack_techniques": dna_info["attack_techniques"],
                "variant_count": 1,
                "community_reports": 0,
                "immunity_protected_count": 1,
                "first_seen": "Today",
                "threat_status": "ACTIVE_CAMPAIGN"
            }

        # 8. Scam Attack Chain Detection & Next-Move Prediction
        attack_chain_info = AttackChainService.evaluate_chain(
            content=content,
            category=category.value,
            urls=url_analyses,
            upi_data=upi_analysis if upi_analysis.get("has_upi_payload") else None
        )

        return {
            "risk_score": final_score,
            "risk_level": risk_level.value,
            "category": category.value,
            "summary": summary,
            "reasons": [r.model_dump() for r in reasons],
            "recommendations": recommendations.model_dump(),
            "urls_detected": url_analyses,
            "technical_details": tech_signals,
            # 6 Signature Features Payload
            "scam_dna": campaign_record,
            "attack_chain": attack_chain_info,
            "next_moves_forecast": attack_chain_info.get("next_moves_forecast", []),
            "upi_safety": upi_analysis,
            "multilingual": multilingual_info
        }

classifier = HybridScamClassifier()
