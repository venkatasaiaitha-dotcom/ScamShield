import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse, parse_qs

class UPIGuard:
    """
    UPI Payment Safety Guard (India-Focused).
    Performs pre-payment safety verification for UPI payment links, QR payloads,
    and message VPA handles before transactions are initiated.
    """

    KNOWN_PSP_HANDLES = {
        'okaxis', 'okhdfcbank', 'okicici', 'oksbi', 'paytm', 'ybl', 'ibl',
        'axl', 'barodampay', 'upi', 'apl', 'airtel', 'federal', 'aubank',
        'kotak', 'indus', 'icici', 'hdfcbank', 'sbi', 'pnb'
    }

    SUSPICIOUS_VPA_KEYWORDS = {
        'refund', 'cashback', 'bonus', 'reward', 'kyc', 'verification',
        'lottery', 'winner', 'fastpay', 'helpline', 'customercare', 'official',
        'support', 'desk', 'urgent', 'instant', 'invest', 'crypto', 'taskpay',
        'refundscam', 'deposit', 'vip'
    }

    ENTITY_VPA_PATTERNS = {
        'sbi': ['sbi', 'statebank'],
        'hdfc': ['hdfc'],
        'icici': ['icici'],
        'axis': ['axis'],
        'amazon': ['amazon', 'amzn'],
        'flipkart': ['flipkart'],
        'electricity': ['bescom', 'tneb', 'mseb', 'uppcl', 'billdesk'],
        'netflix': ['netflix']
    }

    @classmethod
    def analyze(cls, text: str, claimed_brand: Optional[str] = None, qr_payload: Optional[str] = None) -> Dict[str, Any]:
        """
        Parses UPI links or raw text handles and evaluates payment risk.
        """
        target_str = f"{text} {qr_payload or ''}"
        
        extracted_vpas = []
        upi_uri_data = None

        # 1. Parse URI scheme upi://pay?...
        uri_matches = re.findall(r'upi://pay\?[^\s"\'<>]+', target_str, re.IGNORECASE)
        if uri_matches:
            raw_uri = uri_matches[0]
            try:
                parsed = urlparse(raw_uri)
                qs = parse_qs(parsed.query)
                pa = qs.get('pa', [None])[0]
                pn = qs.get('pn', [None])[0]
                am = qs.get('am', [None])[0]
                if pa:
                    extracted_vpas.append(pa)
                    upi_uri_data = {
                        "vpa": pa,
                        "payee_name": pn,
                        "amount": am,
                        "currency": qs.get('cu', ['INR'])[0]
                    }
            except Exception:
                pass

        # 2. Parse text VPA handles: username@handle
        text_vpa_matches = re.findall(r'\b([a-zA-Z0-9.\-_]{2,64}@[a-zA-Z]{2,32})\b', target_str)
        for v in text_vpa_matches:
            v_lower = v.lower()
            handle_suffix = v_lower.split('@')[-1]
            if handle_suffix in cls.KNOWN_PSP_HANDLES or any(h in handle_suffix for h in ['bank', 'pay', 'upi']):
                if v not in extracted_vpas:
                    extracted_vpas.append(v)

        if not extracted_vpas and not upi_uri_data:
            return {
                "has_upi_payload": False,
                "safety_verdict": "NO_PAYMENT_DETECTED",
                "risk_score": 0,
                "vpas": [],
                "reasons": []
            }

        primary_vpa = extracted_vpas[0]
        vpa_user, vpa_psp = primary_vpa.lower().split('@', 1)
        
        risk_score = 10
        reasons = []
        is_mismatch = False
        mismatch_details = None

        # Check Suspicious keywords in username
        flagged_keywords = [kw for kw in cls.SUSPICIOUS_VPA_KEYWORDS if kw in vpa_user]
        if flagged_keywords:
            risk_score += 35
            reasons.append(f"UPI handle contains high-risk bait keyword: '{', '.join(flagged_keywords)}'. Legitimate organizations rarely use generic promotional keywords in primary payment VPAs.")

        # Exclude extracted VPAs from text when detecting claimed brand so @okaxis does not trigger AXIS bank claim
        text_without_vpa = target_str
        for v in extracted_vpas:
            text_without_vpa = text_without_vpa.replace(v, " ")

        # Check Claimed Organization vs VPA Mismatch
        norm_brand = (claimed_brand or '').lower()
        if not norm_brand:
            # Auto-infer claimed brand from message text with word boundary matching
            for e_key, e_pats in cls.ENTITY_VPA_PATTERNS.items():
                if any(re.search(rf"\b{re.escape(p)}\b", text_without_vpa, re.IGNORECASE) for p in e_pats):
                    norm_brand = e_key
                    if not claimed_brand:
                        claimed_brand = e_key.upper()
                    break

        if norm_brand:
            matched_entity_keys = [k for k, pats in cls.ENTITY_VPA_PATTERNS.items() if any(p in norm_brand for p in pats) or k in norm_brand]
            if matched_entity_keys:
                expected_key = matched_entity_keys[0]
                expected_pats = cls.ENTITY_VPA_PATTERNS[expected_key]
                vpa_has_brand = any(p in vpa_user for p in expected_pats)
                
                # If message claims bank or utility, but receiver is a personal handle on generic PSP
                if not vpa_has_brand:
                    is_mismatch = True
                    risk_score += 55
                    mismatch_details = f"Claimed Entity: '{claimed_brand}' | Destination UPI: '{primary_vpa}'"
                    reasons.append(f"Critical Entity-Payment Mismatch: Sender claims to be '{claimed_brand}', but the recipient UPI ID '{primary_vpa}' points to an unverified third-party account.")

        # Urgent coercive language associated with payment
        if any(w in target_str.lower() for w in ["disconnection", "disconnect", "blocked", "cut", "immediate", "penalty", "fine"]):
            risk_score += 15
            reasons.append("High urgency or threat language detected alongside payment demand.")

        # Personal PSP handle check for corporate claims
        if norm_brand and vpa_psp in {'okaxis', 'okhdfcbank', 'okicici', 'oksbi', 'paytm', 'ybl'}:
            if not is_mismatch and not any(k in vpa_user for k in ['official', 'merchant']):
                risk_score += 25
                reasons.append(f"Payment destination is a personal P2P handle (@{vpa_psp}) rather than an authenticated institutional merchant aggregator.")

        risk_score = min(max(risk_score, 10), 98)

        if risk_score >= 65:
            verdict = "HIGH_RISK_DO_NOT_PAY"
            badge_color = "red"
        elif risk_score >= 35:
            verdict = "VERIFY_BEFORE_PAYING"
            badge_color = "amber"
        else:
            verdict = "SAFE"
            badge_color = "green"

        return {
            "has_upi_payload": True,
            "safety_verdict": verdict,
            "badge_color": badge_color,
            "risk_score": risk_score,
            "primary_vpa": primary_vpa,
            "all_vpas": extracted_vpas,
            "uri_data": upi_uri_data,
            "is_mismatch": is_mismatch,
            "mismatch_details": mismatch_details,
            "reasons": reasons,
            "disclaimer": "Pre-payment security safety advisory. ScamShield does not directly execute or block banking rail transactions."
        }
