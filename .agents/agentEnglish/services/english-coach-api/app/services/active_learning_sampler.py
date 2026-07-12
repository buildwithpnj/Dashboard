import uuid
from typing import List
from app.db.models import HardCase
from app.repositories.hard_case_queue import HardCaseQueueRepository

class ActiveLearningSampler:
    """Service class for sampling active learning candidates based on information gain heuristics."""

    def __init__(self, hard_case_repo: HardCaseQueueRepository):
        self.hard_case_repo = hard_case_repo

    async def sample_candidates(
        self, tenant_id: str, product_id: str, candidates: List[dict]
    ) -> List[HardCase]:
        """Filters input candidates based on score range or feedback flags and saves matches as HardCase objects."""
        sampled_cases = []
        for candidate in candidates:
            # Extract score or confidence
            score = candidate.get("composite_score")
            if score is None:
                score = candidate.get("score")
            if score is None:
                score = candidate.get("confidence")

            is_hard = False
            reason = ""
            score_val = 0.0

            if score is not None:
                try:
                    score_val = float(score)
                    if 0.4 <= score_val <= 0.75:
                        is_hard = True
                        reason = f"Low confidence composite score: {score_val:.2f}"
                except (ValueError, TypeError):
                    score_val = 0.0

            # Or if feedback contains high disagreement or repeated dissatisfaction indicators.
            feedback = candidate.get("feedback")
            if not is_hard and feedback:
                if isinstance(feedback, str):
                    f_lower = feedback.lower()
                    if any(term in f_lower for term in ["disagree", "dissatisfied", "unsatisfied", "complaint", "incorrect", "bad", "poor"]):
                        is_hard = True
                        reason = f"Feedback contains dissatisfaction: '{feedback}'"
                elif isinstance(feedback, dict):
                    # Check boolean disagreement/dissatisfaction flags
                    if (
                        feedback.get("disagreement") is True
                        or feedback.get("dissatisfied") is True
                        or feedback.get("dissatisfaction") is True
                    ):
                        is_hard = True
                        reason = "Feedback dict flags disagreement or dissatisfaction"
                    else:
                        # Check for negative sentiment or string values
                        sentiment = feedback.get("sentiment")
                        if sentiment in ["negative", "disagree"]:
                            is_hard = True
                            reason = f"Feedback sentiment is negative: {sentiment}"
                        else:
                            for k, v in feedback.items():
                                if isinstance(v, str):
                                    v_lower = v.lower()
                                    if any(term in v_lower for term in ["disagree", "dissatisfied", "unsatisfied", "complaint", "incorrect", "bad", "poor"]):
                                        is_hard = True
                                        reason = f"Feedback detail '{k}' contains dissatisfaction"
                                        break
                                elif k == "disagreement_score" and isinstance(v, (int, float)) and v > 0.5:
                                    is_hard = True
                                    reason = f"High feedback disagreement score: {v:.2f}"
                                    break

            if is_hard:
                input_text = candidate.get("input_text") or candidate.get("text") or candidate.get("source_text") or candidate.get("utterance") or ""
                priority = 3 if 0.5 <= score_val <= 0.6 else 1


                hard_case = HardCase(
                    id=str(uuid.uuid4()),
                    tenant_id=tenant_id,
                    product_id=product_id,
                    input_text=input_text,
                    reason_sampled=reason or "Active learning sampler match",
                    priority=priority,
                    confidence=score_val,
                    status="PENDING"
                )

                await self.hard_case_repo.create(hard_case)
                sampled_cases.append(hard_case)

        return sampled_cases
