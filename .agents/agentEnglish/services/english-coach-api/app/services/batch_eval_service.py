import uuid
import json
import time
import logging
import datetime
from typing import List, Optional

from app.core.config import settings
from app.db.models import BatchEvalRun, EvalExampleResult
from app.repositories.batch_eval_runs import BatchEvalRunsRepository
from app.repositories.eval_examples import EvalExamplesRepository
from app.services.eval_cost_controller import EvalCostController
from app.services.v8_eval_router import V8EvalRouter

logger = logging.getLogger(__name__)


class BatchEvalService:
    """Orchestrates large-scale dataset evaluation with batching, budgets, and resume.
    
    Features:
    - Streams examples in configurable batch sizes
    - Enforces max budget per run with automatic model downgrade
    - Supports resume from last processed batch via checkpoint
    - Saves per-example results with cost and quality tracking
    """

    def __init__(
        self,
        runs_repo: BatchEvalRunsRepository,
        examples_repo: EvalExamplesRepository,
        eval_router: Optional[V8EvalRouter] = None,
        cost_controller: Optional[EvalCostController] = None,
    ):
        self.runs_repo = runs_repo
        self.examples_repo = examples_repo
        self.eval_router = eval_router or V8EvalRouter()
        self.cost_controller = cost_controller or EvalCostController()

    async def create_run(
        self,
        dataset_name: str,
        product_id: str,
        examples: List[dict],
        budget_limit_usd: Optional[float] = None,
        model_name: str = "mock",
        prompt_version: Optional[str] = None,
        tenant_id: str = "default_tenant"
    ) -> BatchEvalRun:
        """Creates a new batch eval run record capped at MAX_EVAL_EXAMPLES_PER_RUN."""
        max_cap = settings.MAX_EVAL_EXAMPLES_PER_RUN
        capped_count = min(len(examples), max_cap)

        run = BatchEvalRun(
            id=str(uuid.uuid4()),
            dataset_name=dataset_name,
            tenant_id=tenant_id,
            product_id=product_id,
            status="PENDING",
            total_examples=capped_count,
            budget_limit_usd=budget_limit_usd or settings.MAX_EVAL_BUDGET_USD,
            model_name=model_name,
            prompt_version=prompt_version,
        )
        await self.runs_repo.create(run)
        logger.info(f"Created eval run {run.id}: {capped_count} examples (capped from {len(examples)}), budget=${run.budget_limit_usd}")
        return run

    async def execute_run(
        self,
        run_id: str,
        examples: List[dict],
        batch_size: Optional[int] = None,
        resume_from: int = 0,
        mock_model_fn=None,
    ) -> dict:
        """Executes a batch eval run with budget enforcement and resume support.
        
        Args:
            run_id: The eval run ID.
            examples: List of normalized eval example dicts.
            batch_size: Number of examples per batch.
            resume_from: Index to resume processing from.
            mock_model_fn: Optional mock function(input_text) -> str for testing.
            
        Returns:
            Summary dict with run stats.
        """
        run = await self.runs_repo.get_by_id(run_id)
        if not run:
            raise ValueError(f"Run {run_id} not found")

        batch_size = batch_size or settings.EVAL_BATCH_SIZE
        max_cap = settings.MAX_EVAL_EXAMPLES_PER_RUN
        examples = examples[:max_cap]

        # Update run status
        run.status = "RUNNING"
        run.started_at = datetime.datetime.utcnow()
        await self.runs_repo.db.commit()

        # Set budget limit on cost controller
        self.cost_controller.budget_limit_usd = run.budget_limit_usd

        processed = resume_from
        passed = 0
        failed = 0
        budget_stopped = False

        # Process in batches
        while processed < len(examples):
            # Check budget before each batch
            budget_check = self.cost_controller.check_budget()
            if not budget_check["allowed"]:
                logger.warning(f"Budget stop triggered at example {processed}/{len(examples)}")
                budget_stopped = True
                break

            batch_end = min(processed + batch_size, len(examples))
            batch = examples[processed:batch_end]

            results = []
            for example in batch:
                start_time = time.time()

                # Generate model output (mock or real)
                input_text = example.get("source_text", example.get("utterance", ""))
                if mock_model_fn:
                    model_output = mock_model_fn(input_text)
                else:
                    model_output = f"[mock output for: {input_text[:50]}]"

                latency_ms = (time.time() - start_time) * 1000

                # Estimate tokens (rough: 1 token per 4 chars)
                tokens_used = max(1, (len(input_text) + len(model_output)) // 4)

                # Determine model to use based on budget status
                current_model = run.model_name
                if budget_check["action"] == "downgrade":
                    current_model = settings.CHEAP_MODEL_NAME

                # Record cost
                cost = self.cost_controller.record_usage(current_model, tokens_used)

                # Score the example
                scores = self.eval_router.score_example(example, model_output)

                # Compute composite score
                from app.services.scoring.composite_scorer import CompositeScorer
                compositor = CompositeScorer()
                composite_result = compositor.score(
                    task_type=example.get("task_type", ""),
                    dimension_scores=scores,
                    product_id=run.product_id
                )
                composite_score = composite_result.get("composite_score", 0.0)

                # Label errors
                from app.services.error_labeler import ErrorLabeler
                labeler = ErrorLabeler()
                error_bucket = labeler.label(
                    task_type=example.get("task_type", ""),
                    scores=scores,
                    input_text=input_text,
                    model_output=model_output,
                    tokens_used=tokens_used
                )

                is_pass = composite_score >= 0.5
                if is_pass:
                    passed += 1
                else:
                    failed += 1

                # Build result record
                result = EvalExampleResult(
                    id=str(uuid.uuid4()),
                    run_id=run_id,
                    example_hash=example.get("content_hash", example.get("example_id", "")),
                    task_type=example.get("task_type", ""),
                    input_text=input_text,
                    reference_text=json.dumps(
                        example.get("reference_corrections",
                        example.get("target_text",
                        example.get("intent", "")))
                    ),
                    model_output=model_output,
                    composite_score=composite_score,
                    scores_json=json.dumps(scores),
                    model_name=current_model,
                    tokens_used=tokens_used,
                    cost_usd=cost,
                    latency_ms=latency_ms,
                    error_bucket=error_bucket,
                    status="SCORED",
                    prompt_version=run.prompt_version,
                )
                results.append(result)

            # Persist batch
            await self.examples_repo.create_batch(results)
            processed = batch_end

            # Update run progress
            checkpoint = json.dumps({"last_processed_index": processed})
            await self.runs_repo.update_progress(
                run_id=run_id,
                processed_count=processed,
                passed_count=passed,
                failed_count=failed,
                total_tokens=self.cost_controller.cumulative_tokens,
                cost_usd=self.cost_controller.cumulative_cost,
                checkpoint_json=checkpoint
            )
            await self.runs_repo.db.commit()

            logger.info(
                f"Batch complete: {processed}/{len(examples)} processed, "
                f"cost=${self.cost_controller.cumulative_cost:.4f}"
            )

        # Finalize run
        final_status = "BUDGET_STOPPED" if budget_stopped else "COMPLETED"
        await self.runs_repo.complete_run(run_id, status=final_status)
        await self.runs_repo.db.commit()

        summary = {
            "run_id": run_id,
            "status": final_status,
            "total_examples": len(examples),
            "processed": processed,
            "passed": passed,
            "failed": failed,
            **self.cost_controller.get_summary()
        }
        logger.info(f"Run {run_id} finished: {final_status}, processed={processed}, cost=${summary['cumulative_cost_usd']:.4f}")
        return summary
