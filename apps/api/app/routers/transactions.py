import math
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select

from app.deps import DB, CurrentUser
from app.gdrive_sync import sync_section_to_gdrive
from app.models.finance import Account, Category, Transaction
from app.schemas.finance import (
    PaginatedResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionSource,
    TransactionUpdate,
)

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


def _to_response(t: Transaction) -> TransactionResponse:
    return TransactionResponse(
        id=t.id,
        account_id=t.account_id,
        amount=float(t.amount),
        currency=t.currency,
        category_id=t.category_id,
        category_name=t.category.name if t.category else None,
        merchant=t.merchant,
        note=t.note,
        occurred_at=t.occurred_at,
        source=TransactionSource(t.source),
        created_at=t.created_at,
    )


@router.get("", response_model=PaginatedResponse)
async def list_transactions(
    user: CurrentUser,
    db: DB,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    account_id: str | None = None,
    category_id: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    search: str | None = None,
):
    # Base query: only transactions belonging to user's accounts
    user_accounts = select(Account.id).where(Account.user_id == user.id)
    base = select(Transaction).where(Transaction.account_id.in_(user_accounts))

    # Apply filters
    filters = []
    if account_id:
        filters.append(Transaction.account_id == account_id)
    if category_id:
        filters.append(Transaction.category_id == category_id)
    if date_from:
        filters.append(Transaction.occurred_at >= date_from)
    if date_to:
        filters.append(Transaction.occurred_at <= date_to)
    if min_amount is not None:
        filters.append(Transaction.amount >= min_amount)
    if max_amount is not None:
        filters.append(Transaction.amount <= max_amount)
    if search:
        search_filter = or_(
            Transaction.merchant.ilike(f"%{search}%"),
            Transaction.note.ilike(f"%{search}%"),
        )
        filters.append(search_filter)

    if filters:
        base = base.where(and_(*filters))

    # Count total
    count_q = select(func.count()).select_from(base.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Fetch page
    query = (
        base.order_by(Transaction.occurred_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    transactions = result.scalars().all()

    # Eagerly load categories for response
    for t in transactions:
        if t.category_id:
            cat_result = await db.execute(
                select(Category).where(Category.id == t.category_id)
            )
            t.category = cat_result.scalar_one_or_none()

    return PaginatedResponse(
        items=[_to_response(t) for t in transactions],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(body: TransactionCreate, user: CurrentUser, db: DB):
    # Verify account belongs to user
    result = await db.execute(
        select(Account).where(Account.id == body.account_id, Account.user_id == user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    transaction = Transaction(
        account_id=body.account_id,
        amount=body.amount,
        category_id=body.category_id,
        merchant=body.merchant,
        note=body.note,
        source="manual",
    )
    if body.occurred_at:
        transaction.occurred_at = body.occurred_at

    db.add(transaction)
    await db.flush()
    await db.refresh(transaction)
    await sync_section_to_gdrive(user.id, "finance", db)

    # Load category name
    if transaction.category_id:
        cat_result = await db.execute(
            select(Category).where(Category.id == transaction.category_id)
        )
        transaction.category = cat_result.scalar_one_or_none()

    return _to_response(transaction)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str, user: CurrentUser, db: DB):
    user_accounts = select(Account.id).where(Account.user_id == user.id)
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.account_id.in_(user_accounts),
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    if transaction.category_id:
        cat_result = await db.execute(
            select(Category).where(Category.id == transaction.category_id)
        )
        transaction.category = cat_result.scalar_one_or_none()

    return _to_response(transaction)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str, body: TransactionUpdate, user: CurrentUser, db: DB
):
    user_accounts = select(Account.id).where(Account.user_id == user.id)
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.account_id.in_(user_accounts),
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(transaction, field, value)

    await db.flush()
    await db.refresh(transaction)
    await sync_section_to_gdrive(user.id, "finance", db)

    if transaction.category_id:
        cat_result = await db.execute(
            select(Category).where(Category.id == transaction.category_id)
        )
        transaction.category = cat_result.scalar_one_or_none()

    return _to_response(transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(transaction_id: str, user: CurrentUser, db: DB):
    user_accounts = select(Account.id).where(Account.user_id == user.id)
    result = await db.execute(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.account_id.in_(user_accounts),
        )
    )
    transaction = result.scalar_one_or_none()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )

    await db.delete(transaction)
    await sync_section_to_gdrive(user.id, "finance", db)
