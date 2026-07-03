from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import and_, extract, func, select
from sqlalchemy.orm import selectinload

from app.deps import DB, CurrentUser
from app.models.finance import Account, Category, Transaction
from app.schemas.finance import (
    AccountSummary,
    AccountType,
    DashboardSummary,
    SpendingByCategory,
    TransactionResponse,
    TransactionSource,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

CATEGORY_COLORS = [
    "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#06b6d4",
    "#ec4899", "#84cc16", "#f97316", "#6366f1", "#14b8a6",
]


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(user: CurrentUser, db: DB):
    now = datetime.now(UTC)
    current_month = now.month
    current_year = now.year

    # ─── Accounts + balances ──────────────────────────────
    accounts_result = await db.execute(
        select(Account)
        .where(Account.user_id == user.id)
        .options(selectinload(Account.transactions))
    )
    accounts = accounts_result.scalars().all()

    accounts_summary = []
    net_worth = 0.0
    for a in accounts:
        balance = float(a.opening_balance)
        for t in a.transactions:
            balance += float(t.amount)
        balance = round(balance, 2)
        net_worth += balance
        accounts_summary.append(
            AccountSummary(id=a.id, name=a.name, type=AccountType(a.type), balance=balance)
        )

    # ─── This month income + expenses ─────────────────────
    user_accounts = select(Account.id).where(Account.user_id == user.id)

    income_q = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        and_(
            Transaction.account_id.in_(user_accounts),
            Transaction.amount > 0,
            extract("month", Transaction.occurred_at) == current_month,
            extract("year", Transaction.occurred_at) == current_year,
        )
    )
    total_income = float((await db.execute(income_q)).scalar() or 0)

    expense_q = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        and_(
            Transaction.account_id.in_(user_accounts),
            Transaction.amount < 0,
            extract("month", Transaction.occurred_at) == current_month,
            extract("year", Transaction.occurred_at) == current_year,
        )
    )
    total_expenses = abs(float((await db.execute(expense_q)).scalar() or 0))

    # ─── Spending by category ─────────────────────────────
    spending_q = (
        select(Category.name, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            and_(
                Transaction.account_id.in_(user_accounts),
                Transaction.amount < 0,
                extract("month", Transaction.occurred_at) == current_month,
                extract("year", Transaction.occurred_at) == current_year,
            )
        )
        .group_by(Category.name)
        .order_by(func.sum(Transaction.amount).asc())
    )
    spending_result = await db.execute(spending_q)
    spending_by_category = [
        SpendingByCategory(
            category=name,
            amount=abs(float(amount)),
            color=CATEGORY_COLORS[i % len(CATEGORY_COLORS)],
        )
        for i, (name, amount) in enumerate(spending_result.all())
    ]

    # ─── Recent transactions ──────────────────────────────
    recent_q = (
        select(Transaction)
        .where(Transaction.account_id.in_(user_accounts))
        .order_by(Transaction.occurred_at.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_q)
    recent_transactions = []
    for t in recent_result.scalars().all():
        if t.category_id:
            cat_result = await db.execute(
                select(Category).where(Category.id == t.category_id)
            )
            cat = cat_result.scalar_one_or_none()
            cat_name = cat.name if cat else None
        else:
            cat_name = None

        recent_transactions.append(
            TransactionResponse(
                id=t.id,
                account_id=t.account_id,
                amount=float(t.amount),
                currency=t.currency,
                category_id=t.category_id,
                category_name=cat_name,
                merchant=t.merchant,
                note=t.note,
                occurred_at=t.occurred_at,
                source=TransactionSource(t.source),
                created_at=t.created_at,
            )
        )

    return DashboardSummary(
        net_worth=round(net_worth, 2),
        net_worth_change=round(total_income - total_expenses, 2),
        total_income_this_month=round(total_income, 2),
        total_expenses_this_month=round(total_expenses, 2),
        recent_transactions=recent_transactions,
        spending_by_category=spending_by_category,
        accounts_summary=accounts_summary,
    )
