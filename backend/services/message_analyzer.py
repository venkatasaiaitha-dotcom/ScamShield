import re
from typing import Dict, Any, List, Tuple
from ..models.schemas import ScamCategory, RiskLevel, AnalysisReason, ActionRecommendations

# Heuristic pattern definitions
URGENCY_PATTERNS = [
    r'\b(?:immediately|urgent|urgently|within\s+\d+\s*(?:hours|hrs|mins|minutes)|expires?\s+today|today\s+only|act\s+fast|hurry|last\s+chance|before\s+midnight)\b',
    r'\b(?:suspended|blocked|deactivated|terminated|closed)\s+(?:within|today|in\s+\d+)\b'
]

THREATENING_PATTERNS = [
    r'\b(?:account\s+will\s+be\s+blocked|card\s+will\s+be\s+blocked|permanently\s+deleted|legal\s+action|police|arrest|court\s+notice|penalty\s+fee|service\s+cutoff)\b',
    r'\b(?:virus\s+detected|trojan|spyware|compromised|leaked|hacked)\b'
]

FINANCIAL_BAIT_PATTERNS = [
    r'\b(?:earn\s+(?:rs\.?|inr|[₹$€£])?\s*[\d,]+|daily\s+income|guaranteed\s+(?:return|returns|profit|income)|\d+%\s*(?:profit|returns?|daily)|double\s+your\s+money|work\s+from\s+home\s+and\s+earn)\b',
    r'\b(?:won\s+(?:a\s+)?(?:cash\s+)?(?:prize|reward|amount)|lucky\s+draw|cashback\s+reward|congratulations\s+you\s+(?:have\s+)?won|lottery\s+winner|kbc\s+(?:jio\s+)?lucky\s+draw)\b',
    r'\b(?:pay\s+(?:rs\.?|inr|[₹$€£])?\s*[\d,]+\s*(?:registration|kit|activation|security|processing|tax)\s*(?:fee|charge|tax)?)\b',
    r'\b(?:transfer\s+(?:rs\.?|inr|[₹$€£])?\s*[\d,]+.*(?:registration|kit|activation|deposit|fee|to\s+join|vip))\b'
]

FAMILY_EMERGENCY_PATTERNS = [
    r'\b(?:hi\s+mom|hi\s+mum|hello\s+mom|temporary\s+(?:whatsapp|number)|phone\s+fell\s+in\s+water|mic\s+broken|can\'?t\s+call)\b'
]

CREDENTIAL_HARVESTING_PATTERNS = [
    r'\b(?:verify\s+your\s+(?:kyc|pan|aadhaar|account|identity)|update\s+(?:your\s+)?kyc|kyc\s+has\s+expired)\b',
    r'\b(?:enter\s+(?:your\s+)?(?:password|pin|mpin|cvv|otp|card\s+details|netbanking\s+credentials))\b',
    r'\b(?:send\s+(?:me\s+)?(?:the\s+)?otp|share\s+(?:your\s+)?(?:otp|code|pin))\b'
]

IMPERSONATION_SIGNALS = [
    (r'\b(?:sbi|hdfc|icici|axis|pnb|bob|bank\s+of\s+baroda|canara)\b', "Bank Impersonation"),
    (r'\b(?:amazon|flipkart|fedex|dhl|bluedart|delhivery|usps|ups)\b', "E-Commerce / Courier Impersonation"),
    (r'\b(?:netflix|spotify|disney|apple|google|microsoft|meta)\b', "Tech / Streaming Service Impersonation"),
    (r'\b(?:income\s+tax|police|customs|rbi|cbi|government|gov\.in)\b', "Government / Authority Impersonation")
]

SAFE_INFORMATIONAL_PATTERNS = [
    r'\b(?:delivered\s+to|has\s+been\s+delivered|on\s+schedule|boarding\s+at\s+gate|order\s+#\d+|tracking\s+id)\b',
    r'\b(?:valid\s+for\s+\d+\s+minutes?|do\s+not\s+share\s+this\s+otp\s+with\s+anyone|one-time\s+code\s+for\s+signing\s+into)\b'
]

class MessageAnalyzer:
    @staticmethod
    def analyze_text(
        content: str,
        sender: str,
        urls: List[Dict[str, Any]]
    ) -> Tuple[int, ScamCategory, List[AnalysisReason], Dict[str, Any]]:
        lower_content = content.lower()
        reasons: List[AnalysisReason] = []
        technical_signals: Dict[str, Any] = {
            "urgency_detected": False,
            "financial_bait_detected": False,
            "credential_request_detected": False,
            "threatening_detected": False,
            "impersonation_target": None,
            "safe_pattern_matched": False,
            "raw_score_components": {}
        }

        score = 0

        # Step 1: Detect Safe Legitimate transactional context
        is_safe_notification = any(re.search(p, lower_content) for p in SAFE_INFORMATIONAL_PATTERNS)
        if is_safe_notification and len(urls) == 0:
            # Check if this is an authentic incoming OTP notice (e.g. "Do not share OTP" without phishing links)
            if "do not share" in lower_content and ("otp" in lower_content or "code" in lower_content):
                technical_signals["safe_pattern_matched"] = True
                technical_signals["raw_score_components"]["legitimate_security_advice"] = -20
                return (
                    10,
                    ScamCategory.NORMAL,
                    [
                        AnalysisReason(
                            title="Legitimate Security Notice",
                            description="This message provides an authentication code and explicitly cautions against sharing it, with no deceptive links or demands.",
                            severity="LOW"
                        )
                    ],
                    technical_signals
                )
            elif "delivered" in lower_content or "flight" in lower_content or "on schedule" in lower_content:
                technical_signals["safe_pattern_matched"] = True
                return (
                    8,
                    ScamCategory.NORMAL,
                    [
                        AnalysisReason(
                            title="Routine Transactional Update",
                            description="Standard informational dispatch with no urgent demands, financial pressure, or suspicious hyperlinks.",
                            severity="LOW"
                        )
                    ],
                    technical_signals
                )

        # Step 2: Urgency Analysis
        has_urgency = any(re.search(p, lower_content) for p in URGENCY_PATTERNS)
        if has_urgency:
            score += 15
            technical_signals["urgency_detected"] = True
            technical_signals["raw_score_components"]["urgency"] = 15
            reasons.append(AnalysisReason(
                title="Urgency Pressures",
                description="The sender uses artificial time pressure (e.g. 'expires today', 'within 24 hours') to push you into acting without independent thought.",
                severity="HIGH"
            ))

        # Step 3: Threatening Language / Account Blocked
        has_threat = any(re.search(p, lower_content) for p in THREATENING_PATTERNS)
        if has_threat:
            score += 20
            technical_signals["threatening_detected"] = True
            technical_signals["raw_score_components"]["threatening"] = 20
            reasons.append(AnalysisReason(
                title="Threatening Consequences",
                description="Threatens immediate account block, legal penalty, or malware infection to trigger fear.",
                severity="HIGH"
            ))

        # Step 4: Credential / Sensitive Information Request (Fake KYC / Passwords / OTP theft)
        has_credential_request = any(re.search(p, lower_content) for p in CREDENTIAL_HARVESTING_PATTERNS)
        if has_credential_request:
            score += 25
            technical_signals["credential_request_detected"] = True
            technical_signals["raw_score_components"]["credential_request"] = 25
            reasons.append(AnalysisReason(
                title="Sensitive Information Request",
                description="Prompts you to update KYC, credentials, or personal verification data via unofficial mechanisms.",
                severity="HIGH"
            ))

        # Step 5: Financial Bait / Advance Fee / Unrealistic Reward
        has_financial_bait = any(re.search(p, lower_content) for p in FINANCIAL_BAIT_PATTERNS)
        if has_financial_bait:
            score += 30
            technical_signals["financial_bait_detected"] = True
            technical_signals["raw_score_components"]["financial_bait"] = 30
            reasons.append(AnalysisReason(
                title="Financial Bait & Advance Fee",
                description="Promises unrealistic daily earnings, lottery winnings, or requests an upfront registration fee.",
                severity="HIGH"
            ))

        # Step 5b: Family / Emergency Impersonation
        has_family_emergency = any(re.search(p, lower_content) for p in FAMILY_EMERGENCY_PATTERNS)
        if has_family_emergency and any(w in lower_content for w in ["upi", "transfer", "pay", "fee", "money", "rupees", "rs", "exam"]):
            score += 45
            technical_signals["impersonation_target"] = "Family Relative (Hi Mom Scam)"
            reasons.append(AnalysisReason(
                title="WhatsApp Family Impersonation ('Hi Mum' Emergency Trap)",
                description="Attacker pretends to be a close relative using a temporary number due to a broken phone, demanding urgent funds.",
                severity="HIGH"
            ))

        # Step 6: Impersonation Signals
        impersonation_found = None
        for pattern, label in IMPERSONATION_SIGNALS:
            if re.search(pattern, lower_content) or re.search(pattern, sender.lower()):
                impersonation_found = label
                break

        if impersonation_found:
            # If combined with suspicious URL or urgency, it's impersonation
            if len(urls) > 0 or has_urgency or has_threat or has_credential_request:
                score += 20
                technical_signals["impersonation_target"] = impersonation_found
                technical_signals["raw_score_components"]["impersonation"] = 20
                reasons.append(AnalysisReason(
                    title="Brand & Entity Impersonation",
                    description=f"Message claims affiliation with {impersonation_found} to establish counterfeit trust.",
                    severity="HIGH"
                ))

        # Step 7: URL Risk Contribution
        if urls:
            total_url_risk = sum(u.get("risk_contribution", 0) for u in urls)
            url_points = min(total_url_risk, 35)
            score += url_points
            technical_signals["raw_score_components"]["url_analyzer"] = url_points

            for u in urls:
                flags = u.get("suspicious_flags", [])
                if flags:
                    reasons.append(AnalysisReason(
                        title="Suspicious Destination Link",
                        description=f"Link to '{u['domain']}' triggered security flags: {'; '.join(flags[:2])}.",
                        severity="HIGH" if u.get("is_ip_address") or u.get("is_lookalike") else "MEDIUM"
                    ))

        # Step 8: Categorize Scam Type
        category = ScamCategory.NORMAL
        if has_credential_request and ("kyc" in lower_content or "pan" in lower_content or "aadhaar" in lower_content):
            category = ScamCategory.FAKE_KYC
        elif has_financial_bait and ("job" in lower_content or "work from home" in lower_content or "daily" in lower_content):
            category = ScamCategory.JOB_SCAM
        elif has_financial_bait and ("won" in lower_content or "prize" in lower_content or "lucky" in lower_content or "lottery" in lower_content):
            category = ScamCategory.LOTTERY_PRIZE
        elif impersonation_found == "Bank Impersonation" or ("bank" in lower_content and (has_urgency or urls)):
            category = ScamCategory.BANK_IMPERSONATION
        elif "package" in lower_content and ("delivery" in lower_content or "address" in lower_content) and urls:
            category = ScamCategory.DELIVERY_SCAM
        elif "trojan" in lower_content or "virus" in lower_content or "tech support" in lower_content:
            category = ScamCategory.TECH_SUPPORT
        elif "subscription" in lower_content or "account will be" in lower_content or "permanently deleted" in lower_content:
            category = ScamCategory.ACCOUNT_SUSPENSION
        elif has_credential_request or (urls and (has_urgency or impersonation_found)):
            category = ScamCategory.PHISHING
        elif score >= 30:
            category = ScamCategory.SUSPICIOUS_OTHER
        else:
            category = ScamCategory.NORMAL

        # If no reasons were triggered and score is minimal, add normal reassurance
        if not reasons:
            reasons.append(AnalysisReason(
                title="Normal Pattern Alignment",
                description="No aggressive urgency, credential requests, or deceptive links were identified.",
                severity="LOW"
            ))

        capped_score = min(max(score, 5 if category != ScamCategory.NORMAL else 12), 98)
        if category == ScamCategory.NORMAL and not urls and not has_urgency and not has_threat:
            capped_score = min(capped_score, 18)

        return capped_score, category, reasons, technical_signals
