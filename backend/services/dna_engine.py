import hashlib
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

class ScamDNAEngine:
    """
    Scam DNA & Campaign Fingerprinting Engine.
    Generates deterministic structural fingerprints for detected scams,
    identifying lexical variants belonging to the same underlying campaign.
    """

    TECHNIQUE_MAP = {
        "FAKE_KYC": ["T1566.002 Spearphishing Link", "T1586.002 Brand Impersonation", "T1056 Credential Harvesting"],
        "BANK_IMPERSONATION": ["T1586.002 Bank Impersonation", "T1566 Phishing", "T1659 Financial Deception"],
        "JOB_SCAM": ["T1566 Phishing", "T1659 Advance Fee Trap", "T1437 Application Coercion"],
        "LOTTERY_PRIZE": ["T1659 Greed Bait", "T1566 Untargeted Phishing"],
        "WHATSAPP_FAMILY_IMPERSONATION": ["T1586 Human Relationship Impersonation", "T1659 Urgent UPI Trap"],
        "UTILITY_IMPERSONATION": ["T1586 Authority Impersonation", "T1498 Threat of Service Disconnection"],
        "DELIVERY_SCAM": ["T1566.002 Fake Tracking Redirection", "T1586 Courier Impersonation"],
        "UPI_FRAUD": ["T1659 Deceptive UPI Collect", "T1586 Entity Mismatch"],
        "PHISHING": ["T1566 Spearphishing Link", "T1056 Input Capture"]
    }

    @classmethod
    def generate_fingerprint(
        cls,
        content: str,
        sender: str,
        category: str,
        urls: List[Dict[str, Any]],
        upi_data: Optional[Dict[str, Any]] = None,
        impersonation_target: Optional[str] = None
    ) -> Dict[str, Any]:
        lower = content.lower()
        
        # 1. Normalize Brand
        brand = "GENERIC_OR_UNBRANDED"
        if impersonation_target:
            brand = impersonation_target.upper().replace(" ", "_")
        elif "sbi" in lower or "sbi" in sender.lower():
            brand = "SBI_BANK"
        elif "hdfc" in lower or "hdfc" in sender.lower():
            brand = "HDFC_BANK"
        elif "amazon" in lower:
            brand = "AMAZON"
        elif "netflix" in lower:
            brand = "NETFLIX"
        elif "electricity" in lower or "bijli" in lower or "bescom" in lower:
            brand = "ELECTRICITY_BOARD"
        elif "whatsapp" in lower or "hi mom" in lower:
            brand = "WHATSAPP_FAMILY"

        # 2. Urgency Mode
        urgency = "LOW_PRESSURE"
        if any(w in lower for w in ["today", "24 hours", "immediately", "urgent", "turant", "immediate ga"]):
            urgency = "DEADLINE_PRESSURE"
        elif any(w in lower for w in ["blocked", "disconnected", "cutoff", "arrest", "kaat diya", "avvabothundi"]):
            urgency = "PANIC_FEAR"
        elif any(w in lower for w in ["won", "prize", "lottery", "earn", "daily income", "inaam"]):
            urgency = "GREED_REWARD"

        # 3. Payload Type
        payload_type = "TEXT_COERCION"
        if upi_data and upi_data.get("has_upi_payload"):
            payload_type = "UPI_VPA_DIRECT"
        elif urls:
            u0 = urls[0]
            if u0.get("is_ip_address"):
                payload_type = "RAW_IP_ENDPOINT"
            elif u0.get("is_lookalike"):
                payload_type = "HOMOGRAPH_TYPOSQUAT"
            elif u0.get("is_shortener"):
                payload_type = "OBFUSCATED_SHORTENER"
            else:
                payload_type = "PHISHING_URL"

        # 4. Canonical Techniques
        techniques = cls.TECHNIQUE_MAP.get(category, ["T1566 Phishing", "T1659 Social Engineering"])
        if upi_data and upi_data.get("is_mismatch"):
            techniques = list(set(techniques + ["T1659.001 UPI Entity Mismatch"]))

        # 5. Deterministic Hash Formula: BRAND + CATEGORY + URGENCY + PAYLOAD
        seed_string = f"{brand}|{category}|{urgency}|{payload_type}".upper()
        hash_digest = hashlib.sha256(seed_string.encode('utf-8')).hexdigest()[:6].upper()
        
        brand_code = brand[:3]
        cat_code = category[:3]
        dna_hash = f"DNA-{brand_code}-{cat_code}-{payload_type[:3]}-{hash_digest}"
        campaign_id = f"CMP-{brand_code}-{hash_digest}"

        return {
            "campaign_id": campaign_id,
            "dna_hash": dna_hash,
            "scam_type": category,
            "impersonated_brand": brand.replace("_", " "),
            "urgency_style": urgency,
            "payload_type": payload_type,
            "attack_techniques": techniques,
            "threat_status": "ACTIVE_CAMPAIGN"
        }
