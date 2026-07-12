"""
Composite Scorer for V8 Warborn Platform.

Aggregates dimension-level scores into a single weighted composite score
based on task type and product context.
"""

import logging

logger = logging.getLogger(__name__)

# Default dimension weights per task type.
# Each maps dimension_name → weight.  Weights are normalised at scoring time.
TASK_WEIGHTS: dict[str, dict[str, float]] = {
    "correction": {
        "meaning_preservation": 0.30,
        "grammar_quality": 0.35,
        "fluency": 0.20,
        "brevity_control": 0.15,
    },
    "translation": {
        "semantic_preservation": 0.35,
        "naturalness": 0.25,
        "script_handling": 0.20,
        "hinglish_ambiguity": 0.20,
    },
    "intent_routing": {
        "intent_accuracy": 0.50,
        "slot_extraction_quality": 0.30,
        "routing_correctness": 0.20,
    },
}


class CompositeScorer:
    """Combines per-dimension scores into a single weighted composite.

    Uses task-specific weight profiles defined in ``TASK_WEIGHTS`` and
    falls back to equal weighting for unknown task types.
    """

    def score(
        self,
        task_type: str,
        dimension_scores: dict[str, float],
        product_id: str = "english_coach",
    ) -> dict:
        """Compute a weighted composite score.

        Args:
            task_type: One of the keys in ``TASK_WEIGHTS``
                       (e.g., ``"correction"``, ``"translation"``).
            dimension_scores: Mapping of dimension names to their individual
                              scores (each 0.0–1.0).
            product_id: Product identifier for audit / downstream routing.

        Returns:
            Dict containing:
            - ``composite_score``: weighted aggregate (0.0–1.0)
            - ``dimensions``: the original dimension scores
            - ``product_id``: the product context string
        """
        weights = TASK_WEIGHTS.get(task_type)

        if weights is None:
            logger.warning(
                "No weight profile for task_type='%s'; using equal weights.",
                task_type,
            )
            n = len(dimension_scores) or 1
            weights = {dim: 1.0 / n for dim in dimension_scores}

        # Compute weighted sum (only for dimensions present in both dicts)
        total_weight = 0.0
        weighted_sum = 0.0
        for dim, weight in weights.items():
            if dim in dimension_scores:
                weighted_sum += weight * dimension_scores[dim]
                total_weight += weight
            else:
                logger.debug(
                    "Dimension '%s' expected by weights but missing in scores.",
                    dim,
                )

        composite = round(weighted_sum / total_weight, 4) if total_weight else 0.0

        result = {
            "composite_score": composite,
            "dimensions": dict(dimension_scores),
            "product_id": product_id,
        }
        logger.info(
            "CompositeScorer (task=%s, product=%s): composite=%.4f",
            task_type,
            product_id,
            composite,
        )
        return result
