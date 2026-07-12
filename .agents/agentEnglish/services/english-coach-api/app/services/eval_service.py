import json
import logging
from typing import List, Dict, Any
from datetime import datetime

from app.schemas.evals import EvalCase, EvalResult, EvalSummary
from app.schemas.coach import CoachRespondRequest
from app.services.coach_service import CoachService
from app.services.scoring import ScoringEngine
from app.repositories.eval_runs import EvalRunsRepository

logger = logging.getLogger(__name__)

class EvalService:
    """Orchestrates test suite execution and aggregates run summary reports."""

    def __init__(
        self,
        coach_service: CoachService,
        runs_repo: EvalRunsRepository,
        scoring_engine: ScoringEngine
    ):
        self.coach_service = coach_service
        self.runs_repo = runs_repo
        self.scoring_engine = scoring_engine

    def load_cases_from_jsonl(self, file_path: str) -> List[EvalCase]:
        """Reads evaluation cases from a target JSONL test file."""
        cases = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        try:
                            cases.append(EvalCase(**json.loads(stripped)))
                        except Exception as e:
                            logger.error(f"Error parsing case line in {file_path}: {e}")
        except FileNotFoundError:
            logger.warning(f"Eval case file not found: {file_path}")
        return cases

    async def run_eval_cases(self, cases: List[EvalCase], pass_threshold: float = 0.8) -> List[EvalResult]:
        """Executes a batch of test cases and scores them."""
        results = []
        for case in cases:
            # Construct API coach request mock
            req = CoachRespondRequest(
                text=case.input_text,
                session_id=f"eval-session-{case.id}"
            )
            
            # Invoke coach pipeline execution
            response = await self.coach_service.process_request(req)
            
            # Score results
            scores = self.scoring_engine.score_response(case, response)
            weighted_score = self.scoring_engine.calculate_weighted_score(scores)
            passed = weighted_score >= pass_threshold
            
            results.append(
                EvalResult(
                    case_id=case.id,
                    input_text=case.input_text,
                    detected_style=response.detected_input_style,
                    detected_intent=response.intent,
                    actual_ambiguity=response.ambiguity,
                    natural_english=response.natural_english,
                    professional_english=response.professional_english,
                    explanation=response.explanation,
                    scores=scores,
                    weighted_score=weighted_score,
                    passed=passed
                )
            )
        return results

    def compile_summary(self, results: List[EvalResult]) -> EvalSummary:
        """Aggregates test results into summary metrics."""
        total = len(results)
        if total == 0:
            return EvalSummary(
                total_cases=0,
                passed_cases=0,
                failed_cases=0,
                pass_rate=0.0,
                average_weighted_score=0.0,
                dimension_averages={},
                run_timestamp=datetime.utcnow().isoformat()
            )
            
        passed = sum(1 for r in results if r.passed)
        failed = total - passed
        pass_rate = passed / total
        avg_weighted = sum(r.weighted_score for r in results) / total
        
        # Calculate dimension averages
        dim_totals: Dict[str, float] = {}
        for r in results:
            for dim, val in r.scores.items():
                dim_totals[dim] = dim_totals.get(dim, 0.0) + val
                
        dim_averages = {dim: round(val / total, 4) for dim, val in dim_totals.items()}
        
        return EvalSummary(
            total_cases=total,
            passed_cases=passed,
            failed_cases=failed,
            pass_rate=round(pass_rate, 4),
            average_weighted_score=round(avg_weighted, 4),
            dimension_averages=dim_averages,
            run_timestamp=datetime.utcnow().isoformat()
        )

    async def execute_and_log_run(self, eval_files: List[str], pass_threshold: float = 0.8) -> EvalSummary:
        """Executes all cases, aggregates stats, logs outputs to repositories, and returns summary."""
        all_cases = []
        for file in eval_files:
            all_cases.extend(self.load_cases_from_jsonl(file))
            
        results = await self.run_eval_cases(all_cases, pass_threshold=pass_threshold)
        summary = self.compile_summary(results)
        
        # Persist results to repositories output directory
        self.runs_repo.save_run(results, summary)
        
        return summary
