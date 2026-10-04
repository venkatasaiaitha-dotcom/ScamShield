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

        # 6. Check Brand Lookalike / Typosquatting
        is_lookalike = False
        for brand, legit_domains in LEGIT_BRAND_DOMAINS.items():
            if brand in domain_without_port:
                # Is it actually the legit domain?
                is_legit = any(domain_without_port == d or domain_without_port.endswith("." + d) for d in legit_domains)
                if not is_legit:
                    is_lookalike = True
                    flags.append(f"Possible brand spoofing: mimics '{brand.upper()}' on unofficial domain ({domain_without_port})")
                    risk_points += 30
                    break

        # 7. Check Suspicious Path Keywords
        path_matches = [w for w in SUSPICIOUS_PATH_KEYWORDS if w in path]
        if path_matches:
            flags.append(f"Deceptive path elements detected: {', '.join(path_matches)}")
            risk_points += 10

        capped_risk = min(risk_points, 45)

        return {
            "url": url,
            "domain": domain_without_port,
            "is_https": is_https,
            "is_ip_address": is_ip,
            "is_shortener": is_shortener,
            "is_lookalike": is_lookalike,
            "suspicious_flags": flags,
            "risk_contribution": capped_risk
        }
