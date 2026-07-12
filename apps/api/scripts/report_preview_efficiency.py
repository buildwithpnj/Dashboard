import sys
import os

# Append project path to load app packages
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.preview_cost_tuner import PreviewCostTuner

def main():
    report = PreviewCostTuner.get_efficiency_report()
    print("=== PREVIEW COST EFFICIENCY REPORT ===")
    for p_class, stats in report.items():
        print(f"Class: {p_class.upper()}")
        print(f"  Count: {stats['count']}")
        print(f"  Avg Cost (USD): ${stats['avg_cost_usd']:.6f}")
        print(f"  Avg Tokens: {stats['avg_tokens']}")
    print("======================================")

if __name__ == "__main__":
    main()
