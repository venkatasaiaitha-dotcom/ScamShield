import re
import base64
import uuid
from typing import Dict, Any, List, Optional
from .url_analyzer import URLAnalyzer
from ..ml.classifier import classifier

class ImageAnalyzer:
    """
    ScamShield Visual & QR Code Inspector:
    Inspects image payloads, simulated or extracted QR codes, and embedded links
    to detect Quishing (QR Phishing), spoofed payment receipts, and evasive visual scams.
    """
    @classmethod
    def analyze_qr_or_image(
        cls,
        image_data_b64: Optional[str] = None,
        extracted_text: Optional[str] = None,
        qr_payload: Optional[str] = None
    ) -> Dict[str, Any]:
        text_to_analyze = (extracted_text or "").strip()
        qr_content = (qr_payload or "").strip()

        # If base64 provided without explicit QR text, extract simulated metadata or links
        if image_data_b64 and not qr_content and not text_to_analyze:
            try:
                # Basic string scan in raw image bytes if text/links embedded
                decoded_bytes = base64.b64decode(image_data_b64.split(",")[-1])
                raw_str = decoded_bytes[:5000].decode("latin-1", errors="ignore")
                urls = URLAnalyzer.extract_urls(raw_str)
                if urls:
                    qr_content = urls[0]
            except Exception:
                pass

        # If still empty, provide meaningful analysis on provided text
        combined = f"{text_to_analyze}\n{qr_content}".strip()
        if not combined:
            combined = qr_content or "No visible text or QR payload detected."

        detected_urls = URLAnalyzer.extract_urls(combined)
        url_analyses = [URLAnalyzer.analyze_url(u) for u in detected_urls]

        # Process with ScamShield ML & heuristic classifier
        base_result = classifier.process(combined, sender="QR Code / Visual Upload")

        # Quishing-specific risk adjustments
        is_quishing = False
        quishing_flags: List[str] = []

        if qr_content:
            quishing_flags.append("QR Code Payload Extracted")
            if detected_urls:
                is_quishing = True
                quishing_flags.append(f"QR directs to external URL: {detected_urls[0]}")
                # QR codes pointing to login/verify/payment links are high-risk vectors
                if any(u_res.get("risk_contribution", 0) >= 20 for u_res in url_analyses):
                    base_result["risk_score"] = max(base_result.get("risk_score", 0), 88)
                    base_result["risk_level"] = "HIGH"
                    base_result["category"] = "QUISHING_QR_PHISHING"
                    base_result["reasons"].insert(0, {
                        "title": "Quishing Threat (QR Code Phishing)",
                        "description": "Scammers disguise malicious phishing links inside QR codes to bypass email filters and trick mobile users into entering credentials.",
                        "severity": "HIGH"
                    })
                    base_result["recommendations"]["donts"].insert(0, "Do NOT scan or authorize transactions using this QR code")

        return {
            "id": f"img-{uuid.uuid4().hex[:8]}",
            "is_quishing": is_quishing,
            "qr_payload": qr_content or (detected_urls[0] if detected_urls else None),
            "extracted_text": text_to_analyze,
            "detected_urls": detected_urls,
            "url_analysis": url_analyses,
            "risk_score": base_result.get("risk_score", 15),
            "risk_level": base_result.get("risk_level", "LOW"),
            "category": base_result.get("category", "VISUAL_INSPECTION"),
            "summary": base_result.get("summary", "Image and QR payload inspection completed."),
            "reasons": base_result.get("reasons", []),
            "recommendations": base_result.get("recommendations", {}),
            "quishing_flags": quishing_flags
        }
