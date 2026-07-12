import logging
from dataclasses import dataclass, field
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


# Placeholder cost rates per 1K tokens (input+output blended)
MODEL_COST_PER_1K_TOKENS = {
    "gpt-4o": 0.015,
    "gpt-4o-mini": 0.003,
    "gpt-3.5-turbo": 0.0005,
    "mock": 0.0,
}


@dataclass
class EvalCostController:
    """Tracks cumulative cost per eval run and enforces budget stop rules.
    
    Budget policy:
    - At 80% of budget: logs warning and signals model tier downgrade
    - At 100% of budget: hard stops the run and saves checkpoint for resume
    """

    budget_limit_usd: float = field(default_factory=lambda: settings.MAX_EVAL_BUDGET_USD)
    cumulative_cost: float = 0.0
    cumulative_tokens: int = 0
    tier_counts: dict = field(default_factory=lambda: {"cheap": 0, "standard": 0, "premium": 0})
    _downgraded: bool = False

    def estimate_cost(self, model_name: str, tokens: int) -> float:
        """Estimates USD cost for a given model and token count."""
        rate = MODEL_COST_PER_1K_TOKENS.get(model_name, 0.003)
        return round((tokens / 1000.0) * rate, 6)

    def record_usage(self, model_name: str, tokens: int) -> float:
        """Records token usage and returns the incremental cost."""
        cost = self.estimate_cost(model_name, tokens)
        self.cumulative_cost += cost
        self.cumulative_tokens += tokens

        # Track tier counts
        if model_name == settings.PREMIUM_MODEL_NAME:
            self.tier_counts["premium"] += 1
        elif model_name == settings.CHEAP_MODEL_NAME:
            self.tier_counts["cheap"] += 1
        else:
            self.tier_counts["standard"] += 1

        return cost

    def check_budget(self) -> dict:
        """Checks current budget status and returns action directive.
        
        Returns:
            dict with keys:
            - allowed: bool - whether processing can continue
            - action: str - 'continue', 'downgrade', or 'stop'
            - utilization_pct: float - current budget utilization percentage
            - message: str - human-readable status
        """
        if self.budget_limit_usd <= 0:
            return {
                "allowed": True,
                "action": "continue",
                "utilization_pct": 0.0,
                "message": "Budget tracking disabled (limit=0)."
            }

        utilization = (self.cumulative_cost / self.budget_limit_usd) * 100.0

        # Hard stop at 100%
        if self.cumulative_cost >= self.budget_limit_usd:
            logger.error(
                f"BUDGET HARD STOP: ${self.cumulative_cost:.4f} / ${self.budget_limit_usd:.2f} "
                f"({utilization:.1f}%). Run must checkpoint and halt."
            )
            return {
                "allowed": False,
                "action": "stop",
                "utilization_pct": round(utilization, 1),
                "message": f"Budget exhausted: ${self.cumulative_cost:.4f} >= ${self.budget_limit_usd:.2f}"
            }

        # Downgrade warning at 80%
        if utilization >= 80.0 and not self._downgraded:
            self._downgraded = True
            logger.warning(
                f"BUDGET WARNING: ${self.cumulative_cost:.4f} / ${self.budget_limit_usd:.2f} "
                f"({utilization:.1f}%). Switching to cheaper model tier."
            )
            return {
                "allowed": True,
                "action": "downgrade",
                "utilization_pct": round(utilization, 1),
                "message": f"Budget at {utilization:.1f}% — downgrading model tier."
            }

        return {
            "allowed": True,
            "action": "continue",
            "utilization_pct": round(utilization, 1),
            "message": f"Budget healthy: ${self.cumulative_cost:.4f} / ${self.budget_limit_usd:.2f}"
        }

    def get_summary(self) -> dict:
        """Returns a summary of cost tracking state."""
        return {
            "cumulative_cost_usd": round(self.cumulative_cost, 6),
            "cumulative_tokens": self.cumulative_tokens,
            "budget_limit_usd": self.budget_limit_usd,
            "utilization_pct": round(
                (self.cumulative_cost / self.budget_limit_usd * 100) if self.budget_limit_usd > 0 else 0, 1
            ),
            "tier_counts": dict(self.tier_counts),
            "downgraded": self._downgraded
        }
