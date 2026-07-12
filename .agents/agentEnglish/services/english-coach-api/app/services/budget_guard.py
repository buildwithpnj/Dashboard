import logging
from app.repositories.usage_ledger import UsageLedgerRepository
from app.repositories.tenants import TenantsRepository

logger = logging.getLogger(__name__)

class BudgetGuard:
    """Enforces monthly budget limits per tenant, preventing completions requests on breaches."""

    def __init__(self, ledger_repo: UsageLedgerRepository, tenant_repo: TenantsRepository):
        self.ledger_repo = ledger_repo
        self.tenant_repo = tenant_repo

    async def validate_budget(self, tenant_id: str) -> None:
        """Validates current month's aggregate tenant expenditures against their limit."""
        tenant = await self.tenant_repo.get_by_id(tenant_id)
        if not tenant:
            return  # Allow default access if tenant config is unseeded

        monthly_spend = await self.ledger_repo.get_monthly_spend(tenant_id)
        budget_limit = tenant.monthly_budget_usd

        # Check soft budget warning threshold (80% of limit)
        if monthly_spend >= (budget_limit * 0.8):
            logger.warning(
                f"Budget Limit Warning: Tenant {tenant_id} spend is at {monthly_spend:.2f} USD "
                f"of their {budget_limit:.2f} USD monthly cap."
            )
            # Record budget drop metric
            from app.observability.metrics import ObservabilityMetricsTracker
            ObservabilityMetricsTracker.record_budget_drop()

        # Check hard cap budget breach (100% of limit)
        if monthly_spend >= budget_limit:
            logger.error(
                f"Budget Cap Breach: Tenant {tenant_id} hard cap exceeded. "
                f"Spend: {monthly_spend:.2f} / {budget_limit:.2f} USD."
            )
            raise ValueError(f"Monthly spending limit of {budget_limit:.2f} USD exceeded.")
