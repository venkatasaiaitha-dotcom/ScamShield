from typing import Tuple
from ..models.schemas import RiskLevel

class RiskEngine:
    LOW_THRESHOLD = 29
    HIGH_THRESHOLD = 70

    @classmethod
    def evaluate_risk(cls, raw_score: int, custom_high: int = 70, custom_suspicious: int = 30) -> Tuple[int, RiskLevel]:
        """
        Calibrates raw analytical points into a transparent 0-100 risk score and level.
        Requirement #15: Cap the final score at 100 and do not describe it as an exact probability.
        """
        clamped_score = min(max(raw_score, 0), 100)

        if clamped_score >= custom_high:
            level = RiskLevel.HIGH
        elif clamped_score >= custom_suspicious:
            level = RiskLevel.SUSPICIOUS
        else:
            level = RiskLevel.LOW

        return clamped_score, level
