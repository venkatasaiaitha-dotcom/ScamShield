import pytest
from backend.services.benchmark_service import BenchmarkService

def test_benchmark_accuracy_and_metrics():
    """
    Automated benchmark verification test ensuring ScamShield maintains
    high performance on diverse threat vectors and low false positives.
    """
    bench = BenchmarkService.run_benchmark()
    metrics = bench["metrics"]
    perf = bench["performance"]
    telemetry = bench["telemetry_coverage"]

    # Core ML Metrics Standards
    assert metrics["accuracy_pct"] >= 95.0, f"Accuracy dropped below 95%: {metrics['accuracy_pct']}%"
    assert metrics["precision_pct"] >= 95.0, f"Precision dropped below 95%: {metrics['precision_pct']}%"
    assert metrics["recall_pct"] >= 95.0, f"Recall dropped below 95%: {metrics['recall_pct']}%"
    assert metrics["f1_score_pct"] >= 95.0, f"F1-Score dropped below 95%: {metrics['f1_score_pct']}%"
    assert metrics["false_positive_rate_pct"] <= 5.0, f"FPR exceeded 5%: {metrics['false_positive_rate_pct']}%"

    # Latency Standards
    assert perf["mean_latency_ms"] < 50.0, f"Mean latency exceeded 50ms: {perf['mean_latency_ms']}ms"

    # Telemetry Feature Coverage Standards
    assert telemetry["scam_dna_generation_rate_pct"] == 100.0
    assert telemetry["attack_chain_correlation_rate_pct"] == 100.0
    assert telemetry["next_move_forecast_rate_pct"] == 100.0
    assert telemetry["upi_guard_rate_pct"] == 100.0
    assert telemetry["multilingual_detection_rate_pct"] == 100.0

def test_benchmark_dataset_integrity():
    from backend.services.benchmark_service import BENCHMARK_DATASET
    assert len(BENCHMARK_DATASET) >= 30
    scam_count = sum(1 for s in BENCHMARK_DATASET if s["expected_is_scam"])
    benign_count = sum(1 for s in BENCHMARK_DATASET if not s["expected_is_scam"])
    assert scam_count >= 20
    assert benign_count >= 5
