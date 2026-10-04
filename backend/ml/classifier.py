from typing import Dict, Any, List
from ..services.url_analyzer import URLAnalyzer
from ..services.message_analyzer import MessageAnalyzer
from ..services.risk_engine import RiskEngine
from ..services.explanation_engine import ExplanationEngine
from ..models.schemas import RiskLevel, ScamCategory

class HybridScamClassifier:
    """
    Hybrid Classification System:
    Combines rule-based contextual indicators, deep URL analysis,
    and adaptive pattern matching to provide robust zero-dependency offline protection.
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
        # 1. Extract and analyze all URLs
        urls = self.url_analyzer.extract_urls(content)
        url_analyses = [self.url_analyzer.analyze_url(u) for u in urls]

        # 2. NLP & Context-aware message heuristic analysis
        raw_score, category, reasons, tech_signals = self.message_analyzer.analyze_text(
            content=content,
            sender=sender,
            urls=url_analyses
        )

        # 3. Transparent Risk Engine calculation
        final_score, risk_level = self.risk_engine.evaluate_risk(
            raw_score=raw_score,
            custom_high=custom_high_thresh,
            custom_suspicious=custom_susp_thresh
        )

        # 4. Generate Explainable Reasoning and Action Guidance
        summary, recommendations = self.explanation_engine.generate_explanation(
            risk_level=risk_level,
            category=category,
            reasons=reasons,
            urls=url_analyses,
            technical_signals=tech_signals
        )

        return {
            "risk_score": final_score,
            "risk_level": risk_level.value,
            "category": category.value,
            "summary": summary,
            "reasons": [r.model_dump() for r in reasons],
            "recommendations": recommendations.model_dump(),
            "urls_detected": url_analyses,
            "technical_details": tech_signals
        }

classifier = HybridScamClassifier()
