import time
from typing import Dict, Any, List
from ..ml.classifier import classifier
from ..models.schemas import ScamCategory

BENCHMARK_DATASET: List[Dict[str, Any]] = [
    # 1. FAKE_KYC
    {
        "id": "SCAM-KYC-01",
        "sender": "SBI-ALERT",
        "content": "Dear Customer, Your SBI account KYC has expired today. Your NetBanking and ATM card will be blocked within 24 hours. Immediately update your KYC documents at: http://sbi-kyc-verify-portal.in/login",
        "expected_is_scam": True,
        "expected_category": "FAKE_KYC",
        "threat_vector": "Credential Harvesting / Fake KYC"
    },
    {
        "id": "SCAM-KYC-02",
        "sender": "HDFC-BANK",
        "content": "URGENT: Your HDFC bank account is temporarily restricted. Complete your mandatory Aadhaar and PAN KYC verification here: http://hdfc-kyc-service.xyz/verify to prevent suspension.",
        "expected_is_scam": True,
        "expected_category": "FAKE_KYC",
        "threat_vector": "Credential Harvesting / Fake KYC"
    },
    {
        "id": "SCAM-KYC-03",
        "sender": "ICICI-ALERT",
        "content": "Dear ICICI user, your NetBanking access is scheduled for termination. Update your KYC details immediately at http://192.168.1.105/icici/auth.php within 12 hours.",
        "expected_is_scam": True,
        "expected_category": "FAKE_KYC",
        "threat_vector": "Credential Harvesting / Fake KYC"
    },

    # 2. BANK_IMPERSONATION
    {
        "id": "SCAM-BNK-01",
        "sender": "HDFC-NOTIFY",
        "content": "Urgent Security Alert: A debit transaction of ₹49,999 is pending on your HDFC credit card. If you did not authorize this, block your card immediately and verify credentials at http://hdfc-card-protection.xyz/auth",
        "expected_is_scam": True,
        "expected_category": "BANK_IMPERSONATION",
        "threat_vector": "Financial Institution Impersonation"
    },
    {
        "id": "SCAM-BNK-02",
        "sender": "AXIS-FRAUD",
        "content": "Suspicious login detected from Moscow on your Axis Bank NetBanking account. Confirm your identity or your account will be blocked: http://axis-security-check.top/login",
        "expected_is_scam": True,
        "expected_category": "BANK_IMPERSONATION",
        "threat_vector": "Financial Institution Impersonation"
    },

    # 3. UPI_FRAUD (India-Focused)
    {
        "id": "SCAM-UPI-01",
        "sender": "BESCOM-OFFICIAL",
        "content": "Dear BESCOM consumer, pay electricity bill Rs 1,450 to 9876543210@ybl to avoid immediate power disconnection tonight at 9:30 PM.",
        "expected_is_scam": True,
        "expected_category": "UPI_FRAUD",
        "threat_vector": "UPI Payment Trap / Utility Impersonation",
        "has_upi": True
    },
    {
        "id": "SCAM-UPI-02",
        "sender": "+91-91234-56789 (WhatsApp)",
        "content": "Hi Mom, my phone fell in water and got damaged. This is my temporary WhatsApp number. I urgently need to pay my college exam fee ₹15,000 before 5 PM. Can you please transfer to UPI id: college-fees@upi immediately? Can't call mic broken.",
        "expected_is_scam": True,
        "expected_category": "UPI_FRAUD",
        "threat_vector": "WhatsApp Family Emergency Impersonation",
        "has_upi": True
    },
    {
        "id": "SCAM-UPI-03",
        "sender": "REFUND-DESK",
        "content": "Your electricity bill rebate of Rs 2,500 has been approved. Authorize your refund collect request at upi://pay?pa=refundscam@okhdfcbank&pn=RebateCenter&am=2500. Enter UPI PIN to claim.",
        "expected_is_scam": True,
        "expected_category": "UPI_FRAUD",
        "threat_vector": "UPI Deceptive Collect Scam",
        "has_upi": True
    },

    # 4. JOB_SCAM
    {
        "id": "SCAM-JOB-01",
        "sender": "+91-98765-43210",
        "content": "Part-Time Job Opportunity! Earn ₹5,000 to ₹10,000 daily by simply reviewing movie trailers from home. No experience needed. Pay ₹499 registration kit fee to activate your employee ID today via http://bit.ly/quick-daily-cash-jobs",
        "expected_is_scam": True,
        "expected_category": "JOB_SCAM",
        "threat_vector": "Advance Fee / Task Fraud"
    },
    {
        "id": "SCAM-JOB-02",
        "sender": "TELEGRAM-HR",
        "content": "Earn Rs 5,000 daily by liking YouTube videos and rating hotels on Google Maps. No experience needed. Transfer Rs 499 registration fee to taskpay@upi to activate your employee kit.",
        "expected_is_scam": True,
        "expected_category": "JOB_SCAM",
        "threat_vector": "Advance Fee / Task Fraud",
        "has_upi": True
    },
    {
        "id": "SCAM-JOB-03",
        "sender": "GLOBAL-WORK",
        "content": "Amazon hiring online assistants. Work from home and earn 8,000 rupees daily. Pay 999 rupees activation fee to start immediately: http://amazon-hiring-jobs.cc/join",
        "expected_is_scam": True,
        "expected_category": "JOB_SCAM",
        "threat_vector": "Advance Fee / Task Fraud"
    },

    # 5. LOTTERY_PRIZE
    {
        "id": "SCAM-LOT-01",
        "sender": "REWARDS-WIN",
        "content": "Congratulations! Your mobile number was selected in the Annual Lucky Draw! You won a cash prize of ₹50,000. Claim your reward immediately before midnight at http://192.168.10.45/lottery/claim.php",
        "expected_is_scam": True,
        "expected_category": "LOTTERY_PRIZE",
        "threat_vector": "Lottery / Prize Bait"
    },
    {
        "id": "SCAM-LOT-02",
        "sender": "KBC-OFFICIAL",
        "content": "Dear customer, you have won Rs 25,00,000 in KBC Jio Lucky Draw. Contact lottery manager on WhatsApp +919876543210 and pay 2500 processing tax to claim your prize.",
        "expected_is_scam": True,
        "expected_category": "LOTTERY_PRIZE",
        "threat_vector": "Lottery / Prize Bait"
    },

    # 6. DELIVERY_SCAM
    {
        "id": "SCAM-DEL-01",
        "sender": "IN-POST",
        "content": "Your package IN892182049 has been held at the central customs hub due to an incorrect shipping address. Update your delivery address immediately: http://indiapost-parcel-redirection.top/re-deliver",
        "expected_is_scam": True,
        "expected_category": "DELIVERY_SCAM",
        "threat_vector": "Package / Courier Redirection"
    },
    {
        "id": "SCAM-DEL-02",
        "sender": "BLUEDART-EXP",
        "content": "Delivery failed: Package address incomplete. Pay Rs 25 redelivery charge and update address within 24 hours at http://bluedart-courier-express.site/track",
        "expected_is_scam": True,
        "expected_category": "DELIVERY_SCAM",
        "threat_vector": "Package / Courier Redirection"
    },

    # 7. INVESTMENT_SCAM
    {
        "id": "SCAM-INV-01",
        "sender": "VIP-TRADER",
        "content": "Guaranteed 25% daily returns on institutional AI crypto trading. Join our private SEBI registered insider club: http://ai-crypto-vault.xyz/vip. Deposit Rs 5,000 to double your capital in 48h.",
        "expected_is_scam": True,
        "expected_category": "JOB_SCAM", # Financial bait / high-yield fraud
        "threat_vector": "High-Yield Investment / Crypto Scheme"
    },
    {
        "id": "SCAM-INV-02",
        "sender": "STOCK-PRO",
        "content": "Earn 500% profit in 7 days with guaranteed insider stocks tips. Transfer 10,000 to cryptoinvest@upi to join exclusive Telegram VIP signal room.",
        "expected_is_scam": True,
        "expected_category": "UPI_FRAUD",
        "threat_vector": "High-Yield Investment Scheme",
        "has_upi": True
    },

    # 8. ACCOUNT_SUSPENSION / PHISHING
    {
        "id": "SCAM-ACC-01",
        "sender": "WhatsApp-Support",
        "content": "Your WhatsApp account is scheduled to be deactivated within 12 hours due to policy violations. To cancel deactivation and verify your phone number, click: http://whatsapp-support-helpdesk.online/verify",
        "expected_is_scam": True,
        "expected_category": "ACCOUNT_SUSPENSION",
        "threat_vector": "Account Deactivation Scare"
    },
    {
        "id": "SCAM-ACC-02",
        "sender": "NETFLIX-ALERT",
        "content": "Your Netflix membership has expired today. Your subscription will be cancelled unless you update payment details immediately at http://netflix-billing-update.site/pay",
        "expected_is_scam": True,
        "expected_category": "ACCOUNT_SUSPENSION",
        "threat_vector": "Account Deactivation Scare"
    },

    # 9. INDIAN MULTILINGUAL / CODE-MIXED (HINGLISH)
    {
        "id": "SCAM-HIN-01",
        "sender": "SBI-ALERT",
        "content": "Aapka SBI account block ho gaya hai, turant KYC update karein warna 24 ghante mein account permanently band ho jayega: http://sbi-kyc-update.xyz",
        "expected_is_scam": True,
        "expected_category": "FAKE_KYC",
        "threat_vector": "Hinglish Code-Mixed Fake KYC",
        "is_multilingual": True
    },
    {
        "id": "SCAM-HIN-02",
        "sender": "BIJLI-BOARD",
        "content": "Priye upbhokta, aapka bijli connection aaj raat 9:30 baje kaat diya jayega kyunki pichla bill jama nahi hua. Turant bill pay karein 9876543210@ybl par.",
        "expected_is_scam": True,
        "expected_category": "UPI_FRAUD",
        "threat_vector": "Hinglish Code-Mixed Utility Disconnection",
        "is_multilingual": True,
        "has_upi": True
    },

    # 10. INDIAN MULTILINGUAL / CODE-MIXED (TENGLISH)
    {
        "id": "SCAM-TEL-01",
        "sender": "SBI-ALERT",
        "content": "Mee SBI account block avvabothundi, immediate ga KYC update cheyyandi: http://sbi-kyc-update.xyz. Update within 24 hours to prevent permanent deactivation.",
        "expected_is_scam": True,
        "expected_category": "FAKE_KYC",
        "threat_vector": "Tenglish Code-Mixed Fake KYC",
        "is_multilingual": True
    },
    {
        "id": "SCAM-TEL-02",
        "sender": "BESCOM-ALERT",
        "content": "Mee BESCOM power connection immediate ga cut aipothundi. Turant Rs 1,450 pay cheyyandi electricity officer VPA ki: 9876543210@ybl",
        "expected_is_scam": True,
        "expected_category": "UPI_FRAUD",
        "threat_vector": "Tenglish Code-Mixed Utility Disconnection",
        "is_multilingual": True,
        "has_upi": True
    },

    # 11. LEGITIMATE BASELINE MESSAGES (BENIGN SAMPLES)
    {
        "id": "BENIGN-01",
        "sender": "SBI-BANK",
        "content": "INR 450.00 debited from A/c XX1234 at SWIGGY BANGALORE on 08-OCT-26. Avl Bal INR 14,230.50. Call 1800112211 if not done by you.",
        "expected_is_scam": False,
        "expected_category": "NORMAL",
        "threat_vector": "Legitimate Bank Debit Alert"
    },
    {
        "id": "BENIGN-02",
        "sender": "UNIV-SECURE",
        "content": "Your OTP for signing into your student portal is 681042. Valid for 10 minutes. Please do not share this one-time code with anyone for your own security.",
        "expected_is_scam": False,
        "expected_category": "NORMAL",
        "threat_vector": "Legitimate Authentication OTP"
    },
    {
        "id": "BENIGN-03",
        "sender": "AmazonLogistics",
        "content": "Your package containing 'Wireless Bluetooth Earbuds' has been delivered to your receptionist. Tracking ID: AMZ9810428. Thank you for shopping with Amazon.",
        "expected_is_scam": False,
        "expected_category": "NORMAL",
        "threat_vector": "Legitimate Package Delivered Notice"
    },
    {
        "id": "BENIGN-04",
        "sender": "INDIGO-AIR",
        "content": "Flight 6E-204 from Bengaluru to Delhi is on schedule. Boarding at Gate 14 begins at 17:15. Have a pleasant flight.",
        "expected_is_scam": False,
        "expected_category": "NORMAL",
        "threat_vector": "Legitimate Flight Boarding Notice"
    },
    {
        "id": "BENIGN-05",
        "sender": "COLLEGE-OFFICE",
        "content": "The university library will remain open till 11:00 PM during mid-term examination week. Students can access reading rooms with valid college ID.",
        "expected_is_scam": False,
        "expected_category": "NORMAL",
        "threat_vector": "Legitimate Academic Notice"
    },
    {
        "id": "BENIGN-06",
        "sender": "Friend-Rahul",
        "content": "Hey, had a great time at dinner last night! Please send the dinner share of Rs 350 to rahul@okaxis whenever you get a chance.",
        "expected_is_scam": False,
        "expected_category": "NORMAL",
        "threat_vector": "Legitimate P2P Informal UPI Share",
        "has_upi": True
    },
    {
        "id": "BENIGN-07",
        "sender": "APOLLO-CLINIC",
        "content": "Your consultation appointment with Dr. Sharma has been confirmed for tomorrow at 10:30 AM at Indiranagar Clinic. Please arrive 10 minutes prior.",
        "expected_is_scam": False,
        "expected_category": "NORMAL",
        "threat_vector": "Legitimate Healthcare Appointment"
    },
    {
        "id": "BENIGN-08",
        "sender": "ZOMATO-ORDER",
        "content": "Your food order #48192 from Truffles has been picked up by delivery partner Suresh. Hot meals arriving in 20 minutes.",
        "expected_is_scam": False,
        "expected_category": "NORMAL",
        "threat_vector": "Legitimate Food Delivery Tracker"
    }
]

class BenchmarkService:
    """
    Real-Time Benchmark Testing & Scientific Performance Evaluation Suite.
    Runs live inference on diverse attack vectors and benign baselines,
    generating accuracy, precision, recall, F1, latency, and telemetry metrics.
    """

    @classmethod
    def run_benchmark(cls) -> Dict[str, Any]:
        results = []
        latencies_ms = []

        tp = 0
        fp = 0
        tn = 0
        fn = 0

        dna_generated = 0
        attack_chain_mapped = 0
        next_moves_forecasted = 0
        upi_guards_activated = 0
        multilingual_detected = 0

        category_stats: Dict[str, Dict[str, int]] = {}

        for sample in BENCHMARK_DATASET:
            t_start = time.perf_counter()
            res = classifier.process(sample["content"], sample["sender"])
            t_elapsed = (time.perf_counter() - t_start) * 1000
            latencies_ms.append(t_elapsed)

            predicted_is_scam = res["risk_level"] in ["HIGH", "SUSPICIOUS"] or res["risk_score"] >= 30
            actual_is_scam = sample["expected_is_scam"]

            if actual_is_scam and predicted_is_scam:
                tp += 1
                confusion = "TP"
            elif not actual_is_scam and not predicted_is_scam:
                tn += 1
                confusion = "TN"
            elif not actual_is_scam and predicted_is_scam:
                fp += 1
                confusion = "FP"
            else:
                fn += 1
                confusion = "FN"

            # Check Telemetry Features
            has_dna = bool(res.get("scam_dna") and res["scam_dna"].get("dna_hash"))
            has_chain = bool(res.get("attack_chain") and res["attack_chain"].get("attack_chain_detected"))
            has_moves = bool(res.get("next_moves_forecast") and len(res["next_moves_forecast"]) > 0)
            has_upi = bool(res.get("upi_safety") and res["upi_safety"].get("has_upi_payload"))
            is_multi = bool(res.get("multilingual") and res["multilingual"].get("is_multilingual"))

            if has_dna: dna_generated += 1
            if has_chain: attack_chain_mapped += 1
            if has_moves: next_moves_forecasted += 1
            if has_upi: upi_guards_activated += 1
            if is_multi: multilingual_detected += 1

            # Category tracking
            c_label = sample.get("threat_vector", sample["expected_category"])
            if c_label not in category_stats:
                category_stats[c_label] = {"total": 0, "correct": 0}
            category_stats[c_label]["total"] += 1
            if (actual_is_scam == predicted_is_scam):
                category_stats[c_label]["correct"] += 1

            results.append({
                "id": sample["id"],
                "threat_vector": sample["threat_vector"],
                "actual_is_scam": actual_is_scam,
                "predicted_is_scam": predicted_is_scam,
                "predicted_risk_level": res["risk_level"],
                "predicted_score": res["risk_score"],
                "predicted_category": res["category"],
                "latency_ms": round(t_elapsed, 2),
                "confusion": confusion,
                "scam_dna_hash": res.get("scam_dna", {}).get("dna_hash"),
                "kill_chain_stage": res.get("attack_chain", {}).get("current_stage_name"),
                "upi_verdict": res.get("upi_safety", {}).get("safety_verdict"),
                "is_code_mixed": is_multi
            })

        total = len(BENCHMARK_DATASET)
        accuracy = (tp + tn) / total if total else 0.0
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        specificity = tn / (tn + fp) if (tn + fp) else 0.0
        f1_score = (2 * precision * recall) / (precision + recall) if (precision + recall) else 0.0
        fpr = fp / (fp + tn) if (fp + tn) else 0.0
        fnr = fn / (fn + tp) if (fn + tp) else 0.0

        latencies_sorted = sorted(latencies_ms)
        p95_idx = int(0.95 * len(latencies_sorted))

        summary = {
            "total_samples": total,
            "scam_samples": sum(1 for s in BENCHMARK_DATASET if s["expected_is_scam"]),
            "benign_samples": sum(1 for s in BENCHMARK_DATASET if not s["expected_is_scam"]),
            "confusion_matrix": {
                "true_positives": tp,
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn
            },
            "metrics": {
                "accuracy_pct": round(accuracy * 100, 2),
                "precision_pct": round(precision * 100, 2),
                "recall_pct": round(recall * 100, 2),
                "specificity_pct": round(specificity * 100, 2),
                "f1_score_pct": round(f1_score * 100, 2),
                "false_positive_rate_pct": round(fpr * 100, 2),
                "false_negative_rate_pct": round(fnr * 100, 2)
            },
            "performance": {
                "mean_latency_ms": round(sum(latencies_ms) / len(latencies_ms), 2),
                "min_latency_ms": round(min(latencies_ms), 2),
                "max_latency_ms": round(max(latencies_ms), 2),
                "p95_latency_ms": round(latencies_sorted[p95_idx], 2),
                "throughput_msg_per_sec": round(1000.0 / (sum(latencies_ms) / len(latencies_ms)), 1)
            },
            "telemetry_coverage": {
                "scam_dna_generation_rate_pct": round((dna_generated / total) * 100, 1),
                "attack_chain_correlation_rate_pct": round((attack_chain_mapped / total) * 100, 1),
                "next_move_forecast_rate_pct": round((next_moves_forecasted / total) * 100, 1),
                "upi_guard_rate_pct": round((upi_guards_activated / sum(1 for s in BENCHMARK_DATASET if s.get('has_upi'))) * 100, 1),
                "multilingual_detection_rate_pct": round((multilingual_detected / sum(1 for s in BENCHMARK_DATASET if s.get('is_multilingual'))) * 100, 1)
            },
            "category_accuracy": {
                cat: {
                    "accuracy_pct": round((stats["correct"] / stats["total"]) * 100, 1),
                    "samples": stats["total"]
                }
                for cat, stats in category_stats.items()
            },
            "detailed_results": results
        }
        return summary
