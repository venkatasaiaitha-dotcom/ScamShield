#!/usr/bin/env python3
"""
ScamShield Real-Time Benchmark Runner & ML Evaluation Suite.
Executes live inference on diverse threat vectors, measures execution latency,
computes precision, recall, F1, FPR, FNR, and telemetry coverage.
"""
import sys
import json
from pathlib import Path

# Reconfigure stdout for Windows console UTF-8 support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from backend.services.benchmark_service import BenchmarkService

def main():
    print("=" * 80)
    print("🛡️  SCAMSHIELD REAL-TIME BENCHMARKING & MODEL EVALUATION SUITE")
    print("=" * 80)
    print("Executing live inference against all threat vectors and benign baselines...\n")

    bench = BenchmarkService.run_benchmark()

    m = bench["metrics"]
    perf = bench["performance"]
    cm = bench["confusion_matrix"]
    tc = bench["telemetry_coverage"]

    print("📊 1. CLASSIFICATION PERFORMANCE METRICS")
    print("-" * 80)
    print(f"Total Benchmark Samples:      {bench['total_samples']}")
    print(f"  • Ground Truth Scams:       {bench['scam_samples']}")
    print(f"  • Ground Truth Legitimate:  {bench['benign_samples']}")
    print(f"Accuracy:                     {m['accuracy_pct']}%")
    print(f"Precision:                    {m['precision_pct']}%")
    print(f"Recall (Sensitivity):         {m['recall_pct']}%")
    print(f"Specificity:                  {m['specificity_pct']}%")
    print(f"F1-Score:                     {m['f1_score_pct']}%")
    print(f"False Positive Rate (FPR):    {m['false_positive_rate_pct']}%")
    print(f"False Negative Rate (FNR):    {m['false_negative_rate_pct']}%")

    print("\n🔲 2. CONFUSION MATRIX")
    print("-" * 80)
    print(f"True Positives (TP):          {cm['true_positives']} (Confirmed Scams Detected)")
    print(f"True Negatives (TN):          {cm['true_negatives']} (Legitimate Messages Cleared)")
    print(f"False Positives (FP):         {cm['false_positives']} (Benign Wrongly Flagged)")
    print(f"False Negatives (FN):         {cm['false_negatives']} (Scams Missed)")

    print("\n⚡ 3. INFERENCE LATENCY & THROUGHPUT")
    print("-" * 80)
    print(f"Mean Inference Latency:       {perf['mean_latency_ms']} ms / message")
    print(f"Min Latency:                  {perf['min_latency_ms']} ms")
    print(f"Max Latency:                  {perf['max_latency_ms']} ms")
    print(f"95th Percentile (P95):        {perf['p95_latency_ms']} ms")
    print(f"Estimated Throughput:         {perf['throughput_msg_per_sec']} messages / second")

    print("\n🛰️ 4. MULTI-VECTOR SIGNATURE TELEMETRY COVERAGE")
    print("-" * 80)
    print(f"Scam DNA Hash Generation:     {tc['scam_dna_generation_rate_pct']}%")
    print(f"Kill-Chain Attack Mapping:    {tc['attack_chain_correlation_rate_pct']}%")
    print(f"Next-Move Tactical Forecast:  {tc['next_move_forecast_rate_pct']}%")
    print(f"UPI Safety Guard Trigger:     {tc['upi_guard_rate_pct']}%")
    print(f"Indian Multilingual Detect:   {tc['multilingual_detection_rate_pct']}%")

    print("\n🏷️ 5. CATEGORY-BY-CATEGORY ACCURACY BREAKDOWN")
    print("-" * 80)
    print(f"{'Threat Vector / Category':<45} | {'Samples':<8} | {'Accuracy':<10}")
    print("-" * 80)
    for cat, stats in bench["category_accuracy"].items():
        print(f"{cat:<45} | {stats['samples']:<8} | {stats['accuracy_pct']}%")

    # Save output to JSON artifact
    out_file = Path(__file__).parent / "benchmark_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(bench, f, indent=2)
    print("\n" + "=" * 80)
    print(f"✅ Benchmark results exported to: {out_file}")
    print("=" * 80)

if __name__ == "__main__":
    main()
