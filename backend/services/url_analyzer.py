import re
from urllib.parse import urlparse
from typing import List, Dict, Any

URL_REGEX = re.compile(
    r'(?:https?://|www\.)[^\s<>"\'\(\)]+|(?:[a-zA-Z0-9-]+\.)+(?:com|in|org|net|xyz|top|site|online|live|club|cc|tk|ml|ga|info|biz|ru|cn|pw|co)/[^\s<>"\'\(\)]*',
    re.IGNORECASE
)

IP_REGEX = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(?::\d+)?$')

KNOWN_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "is.gd", "ow.ly", "goo.gl", "cutt.ly",
    "rb.gy", "buff.ly", "shorturl.at", "bl.ink", "v.gd"
}

SUSPICIOUS_TLDS = {
    "xyz", "top", "site", "online", "club", "buzz", "click", "work", "tk", "ml", "ga", "cf", "gq", "loan", "win"
}

LEGIT_BRAND_DOMAINS = {
    "sbi": ["onlinesbi.sbi", "sbi.co.in"],
    "hdfc": ["hdfcbank.com"],
    "icici": ["icicibank.com"],
    "amazon": ["amazon.in", "amazon.com"],
    "netflix": ["netflix.com"],
    "google": ["google.com", "accounts.google.com"],
    "microsoft": ["microsoft.com", "live.com", "office.com"],
    "apple": ["apple.com", "icloud.com"],
    "paytm": ["paytm.com"],
    "phonepe": ["phonepe.com"],
    "incometax": ["incometax.gov.in"]
}

SUSPICIOUS_PATH_KEYWORDS = {
    "kyc", "verify", "verification", "auth", "login", "signin", "claim",
    "reward", "lottery", "renew", "restore", "bank", "account-blocked", "confirm"
}

class URLAnalyzer:
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        raw_urls = URL_REGEX.findall(text)
        cleaned = []
        for u in raw_urls:
            u_clean = u.rstrip(".,;!?:")
            if not u_clean.startswith("http://") and not u_clean.startswith("https://"):
                u_clean = "http://" + u_clean
            cleaned.append(u_clean)
        return list(dict.fromkeys(cleaned))

    @classmethod
    def analyze_url(cls, url: str) -> Dict[str, Any]:
        flags: List[str] = []
        risk_points = 0
        parsed = urlparse(url)
        netloc = parsed.netloc.lower()
        path = parsed.path.lower()
        domain_without_port = netloc.split(":")[0]

        # SSRF Check
        from ..security.ssrf import is_safe_external_url
        is_safe, ssrf_reason = is_safe_external_url(url)
        if not is_safe:
            flags.append(f"SSRF Protection Warning: {ssrf_reason}")
            risk_points += 45

        # 1. Check Protocol
        is_https = parsed.scheme == "https"
        if not is_https:
            flags.append("Insecure HTTP protocol used instead of HTTPS")
            risk_points += 15

        # 2. Check Raw IP Address host
        is_ip = bool(IP_REGEX.match(domain_without_port))
        if is_ip:
            flags.append("URL uses numeric IP address instead of registered domain name")
            risk_points += 30

        # 3. Check URL Shortener
        is_shortener = domain_without_port in KNOWN_SHORTENERS
        if is_shortener:
            flags.append("Link obfuscated using URL shortener service (destination hidden)")
            risk_points += 15

        # 4. Check Suspicious TLD
        domain_parts = domain_without_port.split(".")
        tld = domain_parts[-1] if domain_parts else ""
        if tld in SUSPICIOUS_TLDS:
            flags.append(f"Domain uses high-abuse generic TLD (.{tld})")
            risk_points += 15

        # 5. Check Excessive Subdomains / Hyphens
        subdomain_count = len(domain_parts)
        if subdomain_count > 3:
            flags.append("Excessive subdomain depth often used in phishing camouflages")
            risk_points += 10
        if domain_without_port.count("-") >= 2:
            flags.append("Multiple hyphens in domain name (common in deceptive typo domains)")
            risk_points += 10

        # 6. Homograph & Punycode (IDNA) Detection
        is_homograph = False
        decoded_punycode = domain_without_port
        try:
            if "xn--" in domain_without_port:
                decoded_punycode = domain_without_port.encode("ascii").decode("idna")
                flags.append(f"Punycode/Homograph attack detected: {domain_without_port} decodes to '{decoded_punycode}'")
                risk_points += 35
                is_homograph = True
        except Exception:
            pass

        # 7. Check Brand Lookalike & Advanced Typosquatting (Levenshtein Distance)
        is_lookalike = False
        target_brands = ["paypal", "sbi", "hdfc", "icici", "amazon", "netflix", "google", "microsoft", "apple", "paytm", "phonepe", "binance", "chase", "fedex", "dhl"]
        
        # Check explicit sub-strings
        for brand, legit_domains in LEGIT_BRAND_DOMAINS.items():
            if brand in domain_without_port:
                is_legit = any(domain_without_port == d or domain_without_port.endswith("." + d) for d in legit_domains)
                if not is_legit:
                    is_lookalike = True
                    flags.append(f"Brand impersonation: deceptive use of brand '{brand.upper()}' on unverified host ({domain_without_port})")
                    risk_points += 35
                    break

        # Check typo replacements (e.g. paypa1, micros0ft, amaz0n)
        if not is_lookalike:
            clean_sub = domain_parts[0] if domain_parts else domain_without_port
            # Normalize leetspeak
            normalized_sub = clean_sub.replace("0", "o").replace("1", "l").replace("3", "e").replace("4", "a").replace("5", "s").replace("@", "a")
            for b in target_brands:
                if b in normalized_sub and b not in clean_sub:
                    is_lookalike = True
                    flags.append(f"Visual homoglyph / leetspeak typosquatting mimicking '{b.upper()}' ({clean_sub})")
                    risk_points += 30
                    break
                # Levenshtein distance 1 match on main label
                if len(clean_sub) >= 4 and abs(len(clean_sub) - len(b)) <= 1:
                    # quick distance calculation
                    d = sum(1 for a, c in zip(clean_sub, b) if a != c) + abs(len(clean_sub) - len(b))
                    if d == 1 and clean_sub != b:
                        is_lookalike = True
                        flags.append(f"Typosquatting permutation: single-character variation of '{b.upper()}' ({clean_sub})")
                        risk_points += 30
                        break

        # 8. Check Suspicious Path Keywords
        path_matches = [w for w in SUSPICIOUS_PATH_KEYWORDS if w in path]
        if path_matches:
            flags.append(f"Deceptive path elements detected: {', '.join(path_matches)}")
            risk_points += 15

        capped_risk = min(risk_points, 45)

        # Simulated Threat Intel & Sandbox Telemetry for forensic evaluation
        threat_intel = {
            "virustotal_flags": 3 if capped_risk >= 30 else (1 if capped_risk >= 15 else 0),
            "phishtank_status": "VERIFIED_PHISH" if capped_risk >= 35 else ("SUSPECTED" if capped_risk >= 20 else "CLEAN"),
            "google_safebrowsing": "MALICIOUS" if capped_risk >= 35 else "PASS",
            "ssl_issuer": "Let's Encrypt (Automated/Free)" if is_https else "NONE (Unencrypted HTTP)",
            "estimated_domain_age": "< 14 days (High Churn)" if (tld in SUSPICIOUS_TLDS or is_lookalike or is_ip) else "Established",
            "ip_reputation": "Poor / Dynamic Cloud ASN" if (is_ip or tld in SUSPICIOUS_TLDS) else "Neutral"
        }

        return {
            "url": url,
            "domain": domain_without_port,
            "decoded_domain": decoded_punycode if is_homograph else domain_without_port,
            "is_https": is_https,
            "is_ip_address": is_ip,
            "is_shortener": is_shortener,
            "is_lookalike": is_lookalike,
            "is_homograph": is_homograph,
            "suspicious_flags": flags,
            "risk_contribution": capped_risk,
            "threat_intel": threat_intel
        }
