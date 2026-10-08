import re
from typing import Dict, Any, List, Tuple

class MultilingualEngine:
    """
    Indian Multilingual & Code-Mixed Social Engineering Detection Engine.
    Detects urgency, authority threats, and financial baits in:
    - Hinglish (Hindi + English)
    - Tenglish (Telugu + English)
    - Pure Devanagari Hindi
    - Pure Telugu Script
    """

    # Transliterated Hindi / Hinglish keywords
    HINGLISH_URGENCY = [
        r'\b(?:turant|jaldi|aaj\s+raat|aaj\s+hi|bina\s+deri|tatkaal|samay\s+kam)\b',
        r'\b(?:aakhri\s+mauka|aaj\s+aakhri\s+din|24\s+ghante\s+ke\s+andar)\b'
    ]

    HINGLISH_THREATS = [
        r'\b(?:kaat\s+diya\s+jayega|kat\s+jayega|band\s+ho\s+jayega|block\s+ho\s+jayega)\b',
        r'\b(?:khata\s+block|sewa\s+samapt|police\s+karyawahi|kanuni\s+karwayi)\b',
        r'\b(?:bijli\s+kat|connection\s+kat|sim\s+band|line\s+kat)\b'
    ]

    HINGLISH_BAIT = [
        r'\b(?:inaam\s+mila|lottery\s+lagi|ghar\s+baithe\s+kamaye|rozana\s+kamaye)\b',
        r'\b(?:paisa\s+transfer|paise\s+bhejo|advance\s+fees|shulk\s+jama)\b'
    ]

    # Transliterated Telugu / Tenglish keywords
    TENGLISH_URGENCY = [
        r'\b(?:immediate\s*ga|tvaraga|ventane|ippude|ee\s+roju\s+lopo)\b',
        r'\b(?:chivari\s+roju|24\s+gantallo|aakari\s+avakasam)\b'
    ]

    TENGLISH_THREATS = [
        r'\b(?:avvabothundi|block\s+avtundi|aagipothundi|aagipothundhi|raddu\s+avtundi)\b',
        r'\b(?:account\s+block\s+avtundi|khata\s+aagipothundi|current\s+cut\s+avtundi)\b',
        r'\b(?:police\s+case|legal\s+action\s+theesukuntam|card\s+deactivate)\b'
    ]

    TENGLISH_BAIT = [
        r'\b(?:dabbu\s+transfer|dabulu\s+pampandi|lottery\s+vachindi|bahumathi)\b',
        r'\b(?:intlo\s+undi\s+sampadinchandi|rojuku\s+sampadana|udhyogam\s+avakasam)\b'
    ]

    # Devanagari Hindi Script Vectors
    HINDI_SCRIPT_PATTERNS = [
        r'[\u0900-\u097F]+'
    ]

    # Telugu Script Vectors
    TELUGU_SCRIPT_PATTERNS = [
        r'[\u0C00-\u0C7F]+'
    ]

    @classmethod
    def analyze(cls, text: str) -> Dict[str, Any]:
        """
        Analyzes input message for code-mixed Indian social engineering indicators.
        Returns detected dialects, matched signals, and threat contribution.
        """
        lower = text.lower()
        signals: List[Dict[str, str]] = []
        detected_languages: List[str] = ["English"]
        risk_boost = 0

        # Check native scripts
        has_devanagari = any(re.search(p, text) for p in cls.HINDI_SCRIPT_PATTERNS)
        has_telugu_script = any(re.search(p, text) for p in cls.TELUGU_SCRIPT_PATTERNS)

        if has_devanagari:
            detected_languages.append("Hindi (Devanagari)")
            risk_boost += 5
        if has_telugu_script:
            detected_languages.append("Telugu Script")
            risk_boost += 5

        # Check Hinglish patterns
        hinglish_matched = []
        for p in cls.HINGLISH_URGENCY:
            m = re.findall(p, lower)
            if m:
                hinglish_matched.extend(m)
                signals.append({"type": "URGENCY", "term": m[0], "dialect": "Hinglish"})
                risk_boost += 15

        for p in cls.HINGLISH_THREATS:
            m = re.findall(p, lower)
            if m:
                hinglish_matched.extend(m)
                signals.append({"type": "THREAT_CONSEQUENCE", "term": m[0], "dialect": "Hinglish"})
                risk_boost += 20

        for p in cls.HINGLISH_BAIT:
            m = re.findall(p, lower)
            if m:
                hinglish_matched.extend(m)
                signals.append({"type": "FINANCIAL_BAIT", "term": m[0], "dialect": "Hinglish"})
                risk_boost += 20

        if hinglish_matched:
            if "Hinglish (Hindi-English)" not in detected_languages:
                detected_languages.append("Hinglish (Hindi-English)")

        # Check Tenglish patterns
        tenglish_matched = []
        for p in cls.TENGLISH_URGENCY:
            m = re.findall(p, lower)
            if m:
                tenglish_matched.extend(m)
                signals.append({"type": "URGENCY", "term": m[0], "dialect": "Tenglish"})
                risk_boost += 15

        for p in cls.TENGLISH_THREATS:
            m = re.findall(p, lower)
            if m:
                tenglish_matched.extend(m)
                signals.append({"type": "THREAT_CONSEQUENCE", "term": m[0], "dialect": "Tenglish"})
                risk_boost += 20

        for p in cls.TENGLISH_BAIT:
            m = re.findall(p, lower)
            if m:
                tenglish_matched.extend(m)
                signals.append({"type": "FINANCIAL_BAIT", "term": m[0], "dialect": "Tenglish"})
                risk_boost += 20

        if tenglish_matched:
            if "Tenglish (Telugu-English)" not in detected_languages:
                detected_languages.append("Tenglish (Telugu-English)")

        is_code_mixed = len(detected_languages) > 1

        # Infer primary non-English language dialect
        language_mix = "ENGLISH"
        if any("Hindi" in l or "Hinglish" in l for l in detected_languages):
            language_mix = "HINGLISH" if "Hinglish (Hindi-English)" in detected_languages else "DEV_HINDI"
        elif any("Telugu" in l or "Tenglish" in l for l in detected_languages):
            language_mix = "TENGLISH" if "Tenglish (Telugu-English)" in detected_languages else "TELUGU"

        # Check impersonated Indian entities in text
        impersonated_entities = []
        if "sbi" in lower:
            impersonated_entities.append("SBI")
        if "hdfc" in lower:
            impersonated_entities.append("HDFC")
        if "electricity" in lower or "bijli" in lower or "bescom" in lower:
            impersonated_entities.append("ELECTRICITY")
        if "police" in lower or "cbi" in lower or "arrest" in lower:
            impersonated_entities.append("LAW_ENFORCEMENT")

        detected_urgency = any(s["type"] == "URGENCY" for s in signals)
        detected_coercion = any(s["type"] in ["THREAT_CONSEQUENCE", "URGENCY"] for s in signals)

        summary_note = None
        if is_code_mixed:
            summary_note = f"Detected code-mixed message ({', '.join(detected_languages)}). Identifies urgency and deception disguised in regional colloquialisms."

        return {
            "is_code_mixed": is_code_mixed,
            "is_multilingual": is_code_mixed,
            "language_mix": language_mix,
            "detected_languages": detected_languages,
            "matched_signals": signals,
            "detected_urgency": detected_urgency,
            "detected_coercion": detected_coercion,
            "impersonated_entities": impersonated_entities,
            "risk_boost": min(risk_boost, 35),
            "summary_note": summary_note
        }
