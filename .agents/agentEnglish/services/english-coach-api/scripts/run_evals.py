import asyncio
import sys
import os

# Add project root directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.api.deps import get_coach_service, get_llm_provider
from app.services.scoring import ScoringEngine
from app.repositories.eval_runs import EvalRunsRepository
from app.services.eval_service import EvalService

async def main():
    logger_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Resolve active services using standard dependencies wiring
    provider = get_llm_provider()
    coach_service = await get_coach_service(provider=provider)
    runs_repo = EvalRunsRepository(output_dir=os.path.join(logger_dir, "output"))
    scoring_engine = ScoringEngine()

    eval_service = EvalService(
        coach_service=coach_service,
        runs_repo=runs_repo,
        scoring_engine=scoring_engine
    )

    # 2. Define target test dataset files relative to workspace root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    eval_files = [
        os.path.join(base_dir, "data", "evals", "translation_eval.jsonl"),
        os.path.join(base_dir, "data", "evals", "correction_eval.jsonl"),
        os.path.join(base_dir, "data", "evals", "rewrite_eval.jsonl"),
        os.path.join(base_dir, "data", "evals", "ambiguity_eval.jsonl")
    ]

    print("Executing Warborn English Coach Evaluation Suite...")
    print(f"Active Provider: {provider.__class__.__name__} | Model: {settings.MODEL_NAME}")
    print("-" * 60)

    # Threshold from config setting, fallback to 0.8
    threshold = getattr(settings, "EVAL_THRESHOLD", 0.8)

    summary = await eval_service.execute_and_log_run(eval_files, pass_threshold=threshold)

    print("\n" + "=" * 20 + " EVAL SUMMARY " + "=" * 20)
    print(f"Timestamp:              {summary.run_timestamp}")
    print(f"Total Cases Coached:    {summary.total_cases}")
    print(f"Passed Cases:           {summary.passed_cases}")
    print(f"Failed Cases:           {summary.failed_cases}")
    print(f"Pass Rate:              {summary.pass_rate * 100:.2f}%")
    print(f"Avg Weighted Score:     {summary.average_weighted_score:.4f}")
    print("\n--- Dimension Averages ---")
    for dim, avg in summary.dimension_averages.items():
        print(f"{dim:23s} : {avg:.4f}")
    print("=" * 54)

    # Exit with code 1 if below threshold to support CI/CD pipelines
    if summary.pass_rate < threshold:
        print(f"\nFAIL: Pass rate {summary.pass_rate * 100:.2f}% is below target threshold of {threshold * 100:.2f}%", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nPASS: Pass rate {summary.pass_rate * 100:.2f}% satisfies target threshold. Success.")
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main())
