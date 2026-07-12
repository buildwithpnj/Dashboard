import json
import os
import sys

def main():
    # Enforce UTF-8 on Windows terminal streams to support Hindi character displays
    if sys.platform.startswith("win"):
        sys.stdout.reconfigure(encoding='utf-8')
        
    # Paths setup
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(script_dir), "output")

    results_path = os.path.join(output_dir, "eval_results_latest.json")
    summary_path = os.path.join(output_dir, "eval_summary_latest.json")

    if not os.path.exists(results_path) or not os.path.exists(summary_path):
        print("Error: No evaluation runs data found. Please run 'python scripts/run_evals.py' first.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)

        with open(results_path, "r", encoding="utf-8") as f:
            results = json.load(f)
    except Exception as e:
        print(f"Error reading report log files: {e}", file=sys.stderr)
        sys.exit(1)

    # Output formatted report
    print("\n" + "=" * 65)
    print("           WARBORN ENGLISH COACH - ACCURACY EVALUATION REPORT")
    print("=" * 65)
    print(f"Run Completion: {summary['run_timestamp']}")
    print(f"Coached Cases:  {summary['total_cases']} total ({summary['passed_cases']} passed, {summary['failed_cases']} failed)")
    print(f"Pass Success:   {summary['pass_rate'] * 100:.2f}%")
    print(f"Average Index:  {summary['average_weighted_score']:.4f}")
    print("-" * 65)
    print("Dimension Averages:")
    for dim, score in summary['dimension_averages'].items():
        bar = "#" * int(score * 20)
        print(f"  {dim:22s} : {score:.4f}  [{bar:<20}]")
    print("-" * 65)
    
    print(f"{'Case ID':9s} | {'Input Text Preview':32s} | {'Score':6s} | {'Status':6s}")
    print("-" * 65)
    for res in results:
        status_lbl = "PASS" if res['passed'] else "FAIL"
        preview = res['input_text'][:29] + "..." if len(res['input_text']) > 32 else res['input_text']
        print(f"{res['case_id']:9s} | {preview:32s} | {res['weighted_score']:.4f} | {status_lbl:6s}")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    main()
