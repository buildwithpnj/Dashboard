import os
import json

def main():
    results_path = "data/evals/retrieval/retrieval_results.json"
    if not os.path.exists(results_path):
        print(f"Results file not found: {results_path}. Run scripts/run_retrieval_evals.py first.")
        return

    with open(results_path, "r", encoding="utf-8") as f:
        results = json.load(f)

    print("\n=========================================================================")
    print("                      HYBRID RETRIEVAL QUALITY REPORT                    ")
    print("=========================================================================")
    print(f"{'Query':<35} | {'Hit@k':<8} | {'MRR':<6} | {'Precision':<10} | {'Recall':<6}")
    print("-" * 75)

    sum_hit = 0.0
    sum_mrr = 0.0
    sum_prec = 0.0
    sum_rec = 0.0

    for item in results:
        q = item["query"]
        m = item["metrics"]
        
        hit = m.get("hit_at_k", 0.0)
        mrr = m.get("mrr", 0.0)
        prec = m.get("precision", 0.0)
        rec = m.get("recall", 0.0)
        
        sum_hit += hit
        sum_mrr += mrr
        sum_prec += prec
        sum_rec += rec
        
        q_disp = q[:32] + "..." if len(q) > 32 else q
        print(f"{q_disp:<35} | {hit:<8.2f} | {mrr:<6.2f} | {prec:<10.2f} | {rec:<6.2f}")

    total = len(results) or 1
    print("-" * 75)
    print(f"{'Average Metrics':<35} | {sum_hit/total:<8.2f} | {sum_mrr/total:<6.2f} | {sum_prec/total:<10.2f} | {sum_rec/total:<6.2f}")
    print("=========================================================================\n")

if __name__ == "__main__":
    main()
