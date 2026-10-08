import random
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from .base_connector import BaseMessageConnector

DEMO_SCENARIOS = [
    {
        "type": "FAKE_KYC",
        "sender": "SBI-ALERT",
        "content": "Dear Customer, Your SBI account KYC has expired today. Your NetBanking and ATM card will be blocked within 24 hours. Immediately update your KYC documents at: http://sbi-kyc-verify-portal.in/login",
        "label": "Fake KYC Expiry Threat"
    },
    {
        "type": "NORMAL_DELIVERY",
        "sender": "AmazonLogistics",
        "content": "Your package containing 'Wireless Bluetooth Earbuds' has been delivered to your receptionist. Tracking ID: AMZ9810428. Thank you for shopping with Amazon.",
        "label": "Normal Order Delivery"
    },
    {
        "type": "LEGITIMATE_OTP",
        "sender": "UNIV-SECURE",
        "content": "Your OTP for signing into your student portal is 681042. Valid for 10 minutes. Please do not share this one-time code with anyone for your own security.",
        "label": "Legitimate University Portal OTP"
    },
    {
        "type": "JOB_SCAM",
        "sender": "+91-98765-43210",
        "content": "Part-Time Job Opportunity! Earn ₹5,000 to ₹10,000 daily by simply reviewing movie trailers from home. No experience needed. Pay ₹499 registration kit fee to activate your employee ID today via http://bit.ly/quick-daily-cash-jobs",
        "label": "Part-time Job Advance Fee Scam"
    },
    {
        "type": "PRIZE_SCAM",
        "sender": "REWARDS-WIN",
        "content": "Congratulations! Your mobile number was selected in the Annual Lucky Draw! You won a cash prize of ₹50,000. Claim your reward immediately before midnight at http://192.168.10.45/lottery/claim.php",
        "label": "Lottery / Prize Bait Scam"
    },
    {
        "type": "BANK_IMPERSONATION",
        "sender": "HDFC-NOTIFY",
        "content": "Urgent Security Alert: A debit transaction of ₹49,999 is pending on your HDFC credit card. If you did not authorize this, block your card immediately and verify credentials at http://hdfc-card-protection.xyz/auth",
        "label": "Bank Impersonation Phishing"
    },
    {
        "type": "ACCOUNT_SUSPENSION",
        "sender": "NETFLIX-TEAM",
        "content": "Your subscription payment failed. Your Netflix profile and watch history will be permanently deleted unless updated within 12 hours. Update billing now: http://renew-netflix-account.top/pay",
        "label": "Subscription Suspension Threat"
    },
    {
        "type": "TECH_SUPPORT",
        "sender": "+1-888-019-2834",
        "content": "CRITICAL ALERT: Trojan Spyware detected on your computer! Your banking credentials and passwords are being leaked. Call Microsoft Certified Tech Support immediately at 1-800-449-0199 for remote cleanup.",
        "label": "Fake Tech Support Spyware Alert"
    },
    {
        "type": "NORMAL_FLIGHT",
        "sender": "IndiGo-Air",
        "content": "Flight 6E-204 from HYD to BLR is on schedule for boarding at Gate 14 at 19:20. Web check-in completed. Have a pleasant flight.",
        "label": "Flight Boarding Update"
    },
    {
        "type": "WHATSAPP_FAMILY_IMPERSONATION",
        "sender": "+91-91234-56789 (WhatsApp)",
        "content": "Hi Mom, my phone fell in water and got damaged. This is my temporary WhatsApp number. I urgently need to pay my college exam fee ₹15,000 before 5 PM. Can you please transfer to UPI id: college-fees@upi immediately? Can't call mic broken.",
        "label": "WhatsApp 'Hi Mum / Family' Emergency Scam"
    },
    {
        "type": "WHATSAPP_ACCOUNT_TAKEOVER",
        "sender": "WhatsApp-Support (WhatsApp)",
        "content": "Your WhatsApp account is scheduled to be deactivated within 12 hours due to policy violations. To cancel deactivation and verify your phone number, click: http://whatsapp-support-helpdesk.online/verify",
        "label": "WhatsApp Account Takeover Phishing"
    }
]

class DemoConnector(BaseMessageConnector):
    def __init__(self):
        super().__init__(source_id="src-demo", name="Demo Simulator Stream", source_type="DEMO")
        self._connected = True

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> bool:
        self._connected = False
        return True

    def requires_permission(self) -> bool:
        return False

    def permission_status(self) -> str:
        return "GRANTED"

    def receive_message(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": raw_data.get("id", f"msg-{uuid.uuid4().hex[:8]}"),
            "source": "DEMO",
            "sender": raw_data.get("sender", "Demo Simulator"),
            "recipient": raw_data.get("recipient", "User"),
            "content": raw_data.get("content", ""),
            "timestamp": raw_data.get("timestamp", datetime.now().strftime("%I:%M %p")),
            "metadata": raw_data.get("metadata", {})
        }

    def generate_scenario(self, scenario_type: Optional[str] = None) -> Dict[str, Any]:
        """Generates a realistic preset scenario message"""
        if scenario_type and scenario_type.upper() != "RANDOM":
            matched = [s for s in DEMO_SCENARIOS if s["type"].upper() == scenario_type.upper()]
            scenario = matched[0] if matched else random.choice(DEMO_SCENARIOS)
        else:
            scenario = random.choice(DEMO_SCENARIOS)

        return {
            "id": f"msg-{uuid.uuid4().hex[:8]}",
            "source": "DEMO",
            "sender": scenario["sender"],
            "recipient": "You",
            "content": scenario["content"],
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "metadata": {
                "scenario_label": scenario["label"],
                "intended_type": scenario["type"]
            }
        }
