import argparse
import asyncio
import json
import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("run_large_evals")

# Ensure app is on path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.session import AsyncSessionLocal

from app.repositories.batch_eval_runs import BatchEvalRunsRepository
from app.repositories.eval_examples import EvalExamplesRepository
from app.repositories.error_clusters import ErrorClustersRepository
from app.services.batch_eval_service import BatchEvalService
from app.services.failure_bucket_analyzer import FailureBucketAnalyzer
from app.data_ingestion.connectors.dataset_manifest import DatasetManifest
from app.data_ingestion.connectors.license_checker import LicenseChecker
from app.data_ingestion.benchmark_normalizers import normalize_jfleg, normalize_samanantar, normalize_massive
from app.data_ingestion.example_mappers import ExampleMapper

# Mock datasets fallback for offline testing
MOCK_DATASETS = {
    "jfleg": [
        {"sentence": "He go to school yesterday.", "corrections": ["He went to school yesterday.", "He did go to school yesterday."]},
        {"sentence": "I has a apple.", "corrections": ["I have an apple.", "I has an apple."]}
    ],
    "samanantar": [
        {"src": "नमस्ते, आप कैसे हैं?", "tgt": "Hello, how are you?"},
        {"src": "मुझे सेब खाना पसंद है।", "tgt": "I like to eat apples."}
    ],
    "massive": [
        {"utt": "set an alarm for 7 am", "intent": "alarm_set", "annot_utt": "set an alarm for [time : 7 am]"},
        {"utt": "what is the weather in Delhi", "intent": "weather_query", "annot_utt": "what is the weather in [city : Delhi]"}
    ]
}

async def run_evals(args):
    logger.info(f"Starting eval run for dataset={args.dataset}, cap={args.max_examples}, budget=${args.max_budget}")
    
    # Load manifest
    manifest_name = args.dataset
    if manifest_name == "samanantar":
        manifest = DatasetManifest.samanantar_hi()
    elif manifest_name == "jfleg":
        manifest = DatasetManifest.jfleg()
    elif manifest_name == "massive":
        manifest = DatasetManifest.massive()
    else:
        logger.error(f"Unknown dataset {args.dataset}")
        return

    # Check license
    checker = LicenseChecker()
    check_result = checker.validate_manifest(manifest, app_env=settings.APP_ENV)
    if not check_result.get("allowed", True):
        logger.error(f"License check failed for dataset {args.dataset}: {check_result.get('warnings')}")
        return

    # Fetch/load dataset records
    raw_records = []
    try:
        from app.data_ingestion.connectors.hf_loader import HFDatasetLoader
        loader = HFDatasetLoader()
        subset = "hi" if args.dataset == "samanantar" else None
        split = "test"
        raw_records = loader.load(
            dataset_name=manifest.dataset_name,
            subset=subset,
            split=split,
            max_examples=args.max_examples
        )
    except Exception as e:
        logger.warning(f"Failed to load via HuggingFace loader: {e}. Falling back to mock dataset samples.")
        raw_records = MOCK_DATASETS.get(args.dataset, [])

    # Normalize records
    normalized_records = []
    for r in raw_records:
        if args.dataset == "jfleg":
            norm = normalize_jfleg(r)
        elif args.dataset == "samanantar":
            norm = normalize_samanantar(r)
        else:
            norm = normalize_massive(r)
        
        mapped = ExampleMapper.map_to_eval_example(norm, args.dataset)
        normalized_records.append(mapped)

    # Initialize repositories
    async with AsyncSessionLocal() as db:

        runs_repo = BatchEvalRunsRepository(db)
        examples_repo = EvalExamplesRepository(db)
        error_clusters_repo = ErrorClustersRepository(db)
        
        eval_service = BatchEvalService(runs_repo, examples_repo)
        
        # Determine product ID mapping
        product_id = "english_coach"
        if args.dataset == "samanantar":
            product_id = "lifeos_coach"
        elif args.dataset == "massive":
            product_id = "family_checkin"

        # Create execution run record
        run = await eval_service.create_run(
            dataset_name=args.dataset,
            product_id=product_id,
            examples=normalized_records,
            budget_limit_usd=args.max_budget,
            model_name="mock"
        )
        
        # Define mock model logic for offline test compatibility
        def mock_model_fn(input_text):
            if args.dataset == "jfleg":
                return "He went to school yesterday." if "yesterday" in input_text else "I have an apple."
            elif args.dataset == "samanantar":
                return "Hello, how are you?" if "नमस्ते" in input_text else "I like to eat apples."
            else:
                return "alarm_set" if "alarm" in input_text else "weather_query"

        # Execute
        summary = await eval_service.execute_run(
            run_id=run.id,
            examples=normalized_records,
            batch_size=args.batch_size,
            resume_from=args.resume_from,
            mock_model_fn=mock_model_fn
        )

        # Retrieve saved examples to compute failure buckets
        saved_examples = await examples_repo.get_by_run(run.id, limit=1000)
        
        # Aggregate failures
        failure_analyzer = FailureBucketAnalyzer(error_clusters_repo)
        failures = await failure_analyzer.aggregate_failures(
            run_id=run.id,
            results=saved_examples,
            dataset_name=args.dataset,
            model_name="mock",
            product_id=product_id
        )
        await db.commit()

        # Print failure bucket analysis report


        report = failure_analyzer.generate_report(failures, args.dataset, "mock")
        print("\n" + report + "\n")
        logger.info(f"Evaluation complete. Run summary: {summary}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run large-scale dataset evaluations with budget enforcement.")
    parser.add_argument("--dataset", type=str, required=True, choices=["jfleg", "samanantar", "massive"])
    parser.add_argument("--max-examples", type=int, default=1000)
    parser.add_argument("--max-budget", type=float, default=5.0)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--resume-from", type=int, default=0)
    
    args = parser.parse_args()
    asyncio.run(run_evals(args))
