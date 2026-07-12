import logging
from app.prompts.prompt_library import estimate_token_count

logger = logging.getLogger(__name__)

def enforce_context_budget(
    learner_profile: str,
    retrieved_examples: list,
    max_tokens: int
) -> tuple:
    """Clips examples and profile content to comply with the token limit.
    
    Pipes dynamic context segments to ensure stable prompt caching.
    """
    profile_tokens = estimate_token_count(learner_profile)
    examples_tokens = sum(estimate_token_count(ex) for ex in retrieved_examples)
    combined = profile_tokens + examples_tokens

    if combined <= max_tokens:
        return learner_profile, retrieved_examples

    # Record the budget drop occurrence
    from app.observability.metrics import ObservabilityMetricsTracker
    ObservabilityMetricsTracker.record_budget_drop()

    logger.warning(f"Context budget overflow. Tokens: {combined}. Max limit: {max_tokens}. Starting context clip.")

    # Drop examples first (latest retrieved are popped first)
    while retrieved_examples and (estimate_token_count(learner_profile) + sum(estimate_token_count(ex) for ex in retrieved_examples)) > max_tokens:
        dropped = retrieved_examples.pop()
        logger.info(f"Context budget: dropped example '{dropped[:30]}...' to save budget.")

    # Truncate profile summary as fallback
    if estimate_token_count(learner_profile) > max_tokens:
        allowed_chars = max_tokens * 4
        learner_profile = learner_profile[:allowed_chars] + "..."
        logger.warning("Context budget: learner profile summary was truncated.")

    return learner_profile, retrieved_examples
