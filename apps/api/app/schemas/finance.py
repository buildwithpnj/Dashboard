from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AccountType(StrEnum):
    bank = "bank"
    cash = "cash"
    card = "card"
    investment = "investment"


class CategoryKind(StrEnum):
    expense = "expense"
    income = "income"


class BudgetPeriod(StrEnum):
    monthly = "monthly"
    weekly = "weekly"
    yearly = "yearly"


class TransactionSource(StrEnum):
    manual = "manual"
    agent = "agent"


# ─── Account ───────────────────────────────────────────────

class AccountCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: AccountType = AccountType.bank
    currency: str = Field(default="INR", max_length=3)
    opening_balance: float = 0


class AccountUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    type: AccountType | None = None
    currency: str | None = Field(None, max_length=3)


class AccountResponse(BaseModel):
    id: str
    user_id: str
    name: str
    type: AccountType
    currency: str
    opening_balance: float
    current_balance: float = 0
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Category ──────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    parent_id: str | None = None
    kind: CategoryKind = CategoryKind.expense


class CategoryResponse(BaseModel):
    id: str
    name: str
    parent_id: str | None
    kind: CategoryKind
    children: list["CategoryResponse"] = []

    class Config:
        from_attributes = True


# ─── Transaction ───────────────────────────────────────────

class TransactionCreate(BaseModel):
    account_id: str
    amount: float
    category_id: str | None = None
    merchant: str = ""
    note: str = ""
    occurred_at: datetime | None = None


class TransactionUpdate(BaseModel):
    amount: float | None = None
    category_id: str | None = None
    merchant: str | None = None
    note: str | None = None
    occurred_at: datetime | None = None


class TransactionResponse(BaseModel):
    id: str
    account_id: str
    amount: float
    currency: str
    category_id: str | None
    category_name: str | None = None
    merchant: str
    note: str
    occurred_at: datetime
    source: TransactionSource
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionFilters(BaseModel):
    account_id: str | None = None
    category_id: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    min_amount: float | None = None
    max_amount: float | None = None
    search: str | None = None


# ─── Budget ────────────────────────────────────────────────

class BudgetCreate(BaseModel):
    category_id: str
    period: BudgetPeriod = BudgetPeriod.monthly
    amount_limit: float = Field(..., gt=0)


class BudgetUpdate(BaseModel):
    amount_limit: float | None = Field(None, gt=0)
    period: BudgetPeriod | None = None


class BudgetResponse(BaseModel):
    id: str
    category_id: str
    category_name: str | None = None
    period: BudgetPeriod
    amount_limit: float
    spent: float = 0

    class Config:
        from_attributes = True


# ─── Dashboard ─────────────────────────────────────────────

class SpendingByCategory(BaseModel):
    category: str
    amount: float
    color: str


class AccountSummary(BaseModel):
    id: str
    name: str
    type: AccountType
    balance: float


class DashboardSummary(BaseModel):
    net_worth: float
    net_worth_change: float
    total_income_this_month: float
    total_expenses_this_month: float
    recent_transactions: list[TransactionResponse]
    spending_by_category: list[SpendingByCategory]
    accounts_summary: list[AccountSummary]


# ─── Pagination ────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
