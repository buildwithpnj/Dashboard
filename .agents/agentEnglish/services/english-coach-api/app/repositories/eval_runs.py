import json
import os
from typing import List
from app.schemas.evals import EvalResult, EvalSummary

class EvalRunsRepository:
    """Handles saving and logging completed evaluation run summaries to disk."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def save_run(self, results: List[EvalResult], summary: EvalSummary) -> None:
        """Writes current run results and summary statistics to latest logs.
        
        Saves:
        - output/eval_results_latest.json
        - output/eval_summary_latest.json
        """
        results_path = os.path.join(self.output_dir, "eval_results_latest.json")
        summary_path = os.path.join(self.output_dir, "eval_summary_latest.json")

        # Write results list
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump([res.model_dump() for res in results], f, indent=2)

        # Write summary report
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary.model_dump(), f, indent=2)
