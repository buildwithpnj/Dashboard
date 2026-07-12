import os
import sys
import json

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    latest_run_file = os.path.join(script_dir, "data", "evals", "runs", "live_run_latest.json")
    if not os.path.exists(latest_run_file):
        # Fallback to local API folder mapping
        latest_run_file = os.path.join(os.path.dirname(script_dir), "data", "evals", "runs", "live_run_latest.json")
        
    if not os.path.exists(latest_run_file):
        print(f"Error: Evaluation run log file not found at {latest_run_file}. Please run run_live_evals.py first.")
        sys.exit(1)

    with open(latest_run_file, "r", encoding="utf-8") as f:
        run_data = json.load(f)

    # Reconfigure stdout to use UTF-8 encoding on Windows to prevent UnicodeEncodeError
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    print("\n==================================================================")
    print("        WARBORN AGENT PLATFORM - ACCURACY LIVE EVAL REPORT")
    print("==================================================================")
    print(f"Run Completion: {run_data['timestamp']}")
    print(f"Coached Cases:  {run_data['total_cases']} total ({run_data['passed_cases']} passed, {run_data['total_cases'] - run_data['passed_cases']} failed)")
    print(f"Pass Success:   {run_data['pass_rate'] * 100:.2f}%")
    print("-" * 66)
    
    print(f"{'Case ID':10s} | {'Product':15s} | {'Input Text Preview':25s} | {'Score':6s} | {'Status'}")
    print("-" * 66)
    for record in run_data["records"]:
        preview = record["input_text"][:22] + "..." if len(record["input_text"]) > 22 else record["input_text"]
        print(f"{record['id']:10s} | {record['product']:15s} | {preview:25s} | {record['score']:.4f} | {record['status']}")
    print("==================================================================\n")

if __name__ == "__main__":
    main()
