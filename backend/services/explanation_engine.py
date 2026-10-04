from typing import List, Dict, Any, Tuple
from ..models.schemas import RiskLevel, ScamCategory, AnalysisReason, ActionRecommendations

class ExplanationEngine:
    @staticmethod
    def generate_explanation(
        risk_level: RiskLevel,
        category: ScamCategory,
        reasons: List[AnalysisReason],
        urls: List[Dict[str, Any]],
        technical_signals: Dict[str, Any]
    ) -> Tuple[str, ActionRecommendations]:
        """
        Translates raw security indicators into transparent plain-English explanations
        and actionable What Should I Do? (Don'ts and Dos) guidance.
        """
        donts = []
        dos = []

        if risk_level == RiskLevel.HIGH:
            # Construct human summary
            reasons_text = []
            if technical_signals.get("urgency_detected"):
                reasons_text.append("creates artificial urgency")
            if technical_signals.get("credential_request_detected"):
                reasons_text.append("requests sensitive information or authentication data")
            if technical_signals.get("impersonation_target"):
                reasons_text.append(f"appears to impersonate {technical_signals['impersonation_target']}")
            if technical_signals.get("financial_bait_detected"):
                reasons_text.append("offers unrealistic financial rewards or requires advance fees")
            if urls:
                reasons_text.append("contains a link that does not match verified official channels")

            if reasons_text:
                summary = f"This message appears risky because it {', '.join(reasons_text[:3])}."
            else:
                summary = "This message contains multiple indicators commonly associated with digital fraud and impersonation."

            donts = [
                "Click on any links or open attachments in this message",
                "Share one-time passwords (OTP), PINs, or account credentials",
                "Transfer registration fees, advance payments, or security deposits",
                "Call phone numbers provided inside the message body"
            ]
            dos = [
                "Verify directly by typing the official organization website into your browser",
                "Contact customer service using the verified number printed on your physical card or monthly bill",
                "Report this message to your network carrier or digital safety authority"
            ]

        elif risk_level == RiskLevel.SUSPICIOUS:
            summary = "ScamShield noticed some unusual characteristics in this message that warrant caution before interacting."
            donts = [
                "Click links without inspecting the exact destination domain first",
                "Provide sensitive personal identifiers or payment details",
                "Forward this message to other family members or contacts"
            ]
            dos = [
                "Double check the sender address/number against past authentic communications",
                "Log in to your account through the official mobile app to check for genuine alerts"
            ]

        else: # LOW RISK
            if technical_signals.get("safe_pattern_matched"):
                summary = "Standard legitimate communication. No suspicious redirection, credential solicitation, or threat patterns detected."
            else:
                summary = "No major scam indicators detected. The message structure aligns with typical informational messages."

            donts = [
                "Never share private passwords or OTPs even if asked later in subsequent messages"
            ]
            dos = [
                "Keep ScamShield protection active to monitor ongoing correspondence"
            ]

        return summary, ActionRecommendations(donts=donts, dos=dos)
