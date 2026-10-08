from typing import Dict, Any, List, Optional

class AttackChainService:
    """
    Scam Attack Chain Detection & Next-Move Prediction Service.
    Correlates multi-stage adversary tactics along the social engineering kill chain:
    Initial Contact ➔ Trust Building ➔ Credential Theft ➔ Payment Attempt ➔ Account Takeover.
    Predicts adversary next tactical moves with probabilistic confidence.
    """

    STAGES = [
        {"id": "STAGE_1", "name": "Initial Contact", "desc": "Cold lure, smishing message, or unsolicited WhatsApp greeting"},
        {"id": "STAGE_2", "name": "Trust Building", "desc": "Impersonating institutional authority or close family member"},
        {"id": "STAGE_3", "name": "Credential Theft", "desc": "Directing to deceptive portal, fake KYC form, or malicious APK"},
        {"id": "STAGE_4", "name": "Payment Attempt", "desc": "Soliciting direct UPI transfer, advance kit fee, or OTP authorization"},
        {"id": "STAGE_5", "name": "Account Takeover", "desc": "Session hijacking, SIM swap lockout, or unauthorized card debit"}
    ]

    PREDICTION_RULES = {
        "FAKE_KYC": [
            {
                "move": "Credential Harvesting on Counterfeit Web Form",
                "probability": 0.94,
                "defensive_advice": "Never submit passwords, net banking usernames, or card PINs on non-bank domains."
            },
            {
                "move": "Urgent Follow-Up SMS or Call Demanding OTP",
                "probability": 0.88,
                "defensive_advice": "Official bank representatives never call to ask for OTPs or SMS security codes."
            },
            {
                "move": "Simulated Account Lockout Threat Escalation",
                "probability": 0.76,
                "defensive_advice": "Do not panic; verify your account status through the official mobile banking app."
            }
        ],
        "WHATSAPP_FAMILY_IMPERSONATION": [
            {
                "move": "Sending Direct UPI ID / QR Code for Instant Transfer",
                "probability": 0.95,
                "defensive_advice": "Do not transfer money to new UPI VPAs before speaking directly on the phone."
            },
            {
                "move": "Fabricating Medical or Emergency Excuse to Prevent Calling",
                "probability": 0.89,
                "defensive_advice": "Immediately call your family member on their known existing phone number."
            }
        ],
        "JOB_SCAM": [
            {
                "move": "Small Payout (₹100–₹500) to Establish Fake Trust",
                "probability": 0.91,
                "defensive_advice": "Scammers often pay small amounts first to lure victims into high-value deposits."
            },
            {
                "move": "Demanding Mandatory ₹2,000–₹10,000 'VIP Task Deposit'",
                "probability": 0.96,
                "defensive_advice": "Legitimate employers never ask employees to pay security fees to work."
            }
        ],
        "DEFAULT": [
            {
                "move": "Escalation to High-Urgency Payment or OTP Lure",
                "probability": 0.82,
                "defensive_advice": "Block the sender and verify independently with the official entity."
            },
            {
                "move": "Alternative Contact via Telegram or WhatsApp",
                "probability": 0.74,
                "defensive_advice": "Avoid continuing conversations on encrypted private messaging platforms."
            }
        ]
    }

    @classmethod
    def evaluate_chain(
        cls,
        content: str,
        category: str,
        urls: List[Dict[str, Any]],
        upi_data: Optional[Dict[str, Any]] = None,
        previous_stages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        lower = content.lower()
        
        # Determine Current Stage
        if upi_data and upi_data.get("has_upi_payload"):
            current_stage_id = "STAGE_4"
            current_stage_name = "Payment Attempt"
        elif "otp" in lower and any(w in lower for w in ["share", "send", "tell", "bhejo"]):
            current_stage_id = "STAGE_4"
            current_stage_name = "Payment Attempt"
        elif urls or "kyc" in lower or "pan" in lower or "login" in lower or "verify" in lower:
            current_stage_id = "STAGE_3"
            current_stage_name = "Credential Theft"
        elif any(w in lower for w in ["bank", "sbi", "hdfc", "amazon", "officer", "mom", "mum", "support"]):
            current_stage_id = "STAGE_2"
            current_stage_name = "Trust Building"
        else:
            current_stage_id = "STAGE_1"
            current_stage_name = "Initial Contact"

        # Determine Stages Timeline
        active_idx = next((i for i, s in enumerate(cls.STAGES) if s["id"] == current_stage_id), 0)
        
        stages_progression = []
        for i, s in enumerate(cls.STAGES):
            if i < active_idx:
                status = "COMPLETED"
            elif i == active_idx:
                status = "ACTIVE_DETECTED"
            else:
                status = "PREDICTED_FUTURE"
            
            stages_progression.append({
                "stage_id": s["id"],
                "name": s["name"],
                "description": s["desc"],
                "status": status,
                "is_current": (i == active_idx)
            })

        # Predict Next Moves
        raw_predictions = cls.PREDICTION_RULES.get(category, cls.PREDICTION_RULES["DEFAULT"])
        predicted_next = cls.STAGES[min(active_idx + 1, len(cls.STAGES) - 1)]["name"]

        formatted_predictions = []
        for p in raw_predictions:
            formatted_predictions.append({
                "move": p["move"],
                "predicted_move": p["move"],
                "probability": p["probability"],
                "probability_pct": int(p["probability"] * 100),
                "defensive_advice": p["defensive_advice"],
                "prevention_tip": p["defensive_advice"]
            })

        return {
            "attack_chain_detected": True,
            "current_stage_id": current_stage_id,
            "current_stage_name": current_stage_name,
            "predicted_next_stage": predicted_next,
            "stages_timeline": stages_progression,
            "next_moves_forecast": formatted_predictions,
            "chain_narrative": f"Current Attack Stage: {current_stage_name}. The attacker is advancing along the social engineering kill chain toward {predicted_next}."
        }
