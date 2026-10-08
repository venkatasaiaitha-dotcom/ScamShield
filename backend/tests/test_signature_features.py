import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.ml.classifier import classifier
from backend.services.multilingual_engine import MultilingualEngine
from backend.services.upi_guard import UPIGuard
from backend.services.dna_engine import ScamDNAEngine
from backend.services.attack_chain_service import AttackChainService
from backend.database.connection import get_campaigns, record_or_update_campaign

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def auth_headers(client):
    resp = client.post("/api/auth/login", json={
        "email": "user@scamshield.local",
        "password": "UserSafe2026!"
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# 1. Indian Multilingual + Code-Mixed Detection
def test_multilingual_code_mixed_hinglish():
    msg = "Aapka SBI account block ho gaya hai, turant KYC update karein warna bijli kaat di jayegi."
    res = MultilingualEngine.analyze(msg)
    assert res["is_multilingual"] is True
    assert res["language_mix"] in ["HINGLISH", "DEV_HINDI"]
    assert res["detected_urgency"] is True
    assert "SBI" in res["impersonated_entities"] or "ELECTRICITY" in res["impersonated_entities"]

def test_multilingual_code_mixed_tenglish():
    msg = "Mee SBI account block avvabothundi, immediate ga KYC update cheyyandi."
    res = MultilingualEngine.analyze(msg)
    assert res["is_multilingual"] is True
    assert res["language_mix"] in ["TENGLISH", "TELUGU"]
    assert res["detected_urgency"] is True
    assert res["detected_coercion"] is True

# 2. UPI Payment Safety Guard
def test_upi_guard_safe_vpa():
    res = UPIGuard.analyze("Please send the dinner share to rahul@okaxis")
    assert res["has_upi_payload"] is True
    assert res["primary_vpa"] == "rahul@okaxis"
    assert res["safety_verdict"] == "SAFE"

def test_upi_guard_brand_mismatch_flagged():
    # Message claims to be Electricity bill / BESCOM, but VPA is a personal phone number handle
    msg = "Dear BESCOM consumer, pay electricity bill Rs 1450 to 9876543210@ybl to avoid immediate power disconnection."
    res = UPIGuard.analyze(msg)
    assert res["has_upi_payload"] is True
    assert res["is_mismatch"] is True
    assert res["safety_verdict"] == "HIGH_RISK_DO_NOT_PAY"
    assert len(res["reasons"]) > 0

# 3. Scam DNA / Fingerprinting Engine
def test_scam_dna_fingerprinting():
    dna1 = ScamDNAEngine.generate_fingerprint(
        content="URGENT: SBI NetBanking suspended. Update KYC now at http://sbi-kyc-verify.cc",
        sender="SBI-ALERT",
        category="FAKE_KYC",
        urls=[{"url": "http://sbi-kyc-verify.cc", "is_ip_address": False, "is_lookalike": True}]
    )
    assert dna1["campaign_id"].startswith("CMP-")
    assert dna1["dna_hash"].startswith("DNA-")
    assert dna1["impersonated_brand"] == "SBI BANK"
    assert len(dna1["attack_techniques"]) > 0

    # Variant with slightly different wording should generate consistent DNA
    dna2 = ScamDNAEngine.generate_fingerprint(
        content="Dear customer, your SBI account is suspended. Verify KYC immediately at http://sbi-kyc-portal.cc",
        sender="+919876543210",
        category="FAKE_KYC",
        urls=[{"url": "http://sbi-kyc-portal.cc", "is_ip_address": False, "is_lookalike": True}]
    )
    assert dna1["campaign_id"] == dna2["campaign_id"]
    assert dna1["dna_hash"] == dna2["dna_hash"]

# 4. Scam Attack Chain Detection & Next-Move Prediction
def test_attack_chain_progression_and_prediction():
    res = classifier.process(
        content="Mee SBI account block avvabothundi, immediate ga KYC update cheyyandi: http://sbi-update.xyz. Enter OTP and netbanking password to unfreeze.",
        sender="SBI-ALERT"
    )
    assert "attack_chain" in res
    assert "scam_dna" in res
    assert "next_moves_forecast" in res
    chain = res["attack_chain"]
    assert chain["current_stage_name"] in ["Initial Contact", "Credential Theft", "Payment Attempt", "Trust Building"]
    assert len(chain["stages_timeline"]) == 5
    assert len(res["next_moves_forecast"]) >= 2
    # Ensure next moves have probabilities and safety tips
    for move in res["next_moves_forecast"]:
        assert "predicted_move" in move
        assert "probability_pct" in move
        assert "prevention_tip" in move

# 5. Expo Drill Scenarios API & Campaigns API
def test_expo_drill_scenarios_endpoint(client, auth_headers):
    resp = client.get("/api/expo/drills", headers=auth_headers)
    assert resp.status_code == 200
    drills = resp.json()
    assert len(drills) == 5
    drill_ids = [d["id"] for d in drills]
    assert "DRILL_FAKE_KYC" in drill_ids
    assert "DRILL_UPI_SCAM" in drill_ids
    assert "DRILL_JOB_SCAM" in drill_ids
    assert "DRILL_COURIER_SCAM" in drill_ids
    assert "DRILL_INVESTMENT_SCAM" in drill_ids

def test_campaigns_endpoint(client, auth_headers):
    resp = client.get("/api/campaigns", headers=auth_headers)
    assert resp.status_code == 200
    campaigns = resp.json()
    assert isinstance(campaigns, list)
    assert len(campaigns) > 0
    c0 = campaigns[0]
    assert "campaign_id" in c0 or "id" in c0
    assert "dna_hash" in c0
    assert "immunity_protected_count" in c0
