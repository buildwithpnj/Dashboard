from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import DB, CurrentUser
from app.gdrive_sync import sync_section_to_gdrive
from app.models.finance import Account
from app.schemas.finance import AccountCreate, AccountResponse, AccountType, AccountUpdate

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


def _compute_balance(account: Account) -> float:
    """Compute current balance from opening balance + sum of transactions."""
    total = float(account.opening_balance)
    if account.transactions:
        for t in account.transactions:
            total += float(t.amount)
    return round(total, 2)


@router.get("", response_model=list[AccountResponse])
async def list_accounts(user: CurrentUser, db: DB):
    result = await db.execute(
        select(Account)
        .where(Account.user_id == user.id)
        .options(selectinload(Account.transactions))
        .order_by(Account.created_at.desc())
    )
    accounts = result.scalars().all()
    return [
        AccountResponse(
            id=a.id,
            user_id=a.user_id,
            name=a.name,
            type=AccountType(a.type),
            currency=a.currency,
            opening_balance=float(a.opening_balance),
            current_balance=_compute_balance(a),
            created_at=a.created_at,
        )
        for a in accounts
    ]


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(body: AccountCreate, user: CurrentUser, db: DB):
    account = Account(
        user_id=user.id,
        name=body.name,
        type=body.type.value,
        currency=body.currency,
        opening_balance=body.opening_balance,
    )
    db.add(account)
    await db.flush()
    await db.refresh(account)
    await sync_section_to_gdrive(user.id, "finance", db)

    return AccountResponse(
        id=account.id,
        user_id=account.user_id,
        name=account.name,
        type=AccountType(account.type),
        currency=account.currency,
        opening_balance=float(account.opening_balance),
        current_balance=float(account.opening_balance),
        created_at=account.created_at,
    )


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: str, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Account)
        .where(Account.id == account_id, Account.user_id == user.id)
        .options(selectinload(Account.transactions))
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    return AccountResponse(
        id=account.id,
        user_id=account.user_id,
        name=account.name,
        type=AccountType(account.type),
        currency=account.currency,
        opening_balance=float(account.opening_balance),
        current_balance=_compute_balance(account),
        created_at=account.created_at,
    )


@router.patch("/{account_id}", response_model=AccountResponse)
async def update_account(account_id: str, body: AccountUpdate, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(account, field, value)

    await db.flush()
    await db.refresh(account)
    await sync_section_to_gdrive(user.id, "finance", db)

    return AccountResponse(
        id=account.id,
        user_id=account.user_id,
        name=account.name,
        type=AccountType(account.type),
        currency=account.currency,
        opening_balance=float(account.opening_balance),
        current_balance=float(account.opening_balance),
        created_at=account.created_at,
    )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: str, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Account).where(Account.id == account_id, Account.user_id == user.id)
    )
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    await db.delete(account)
    await sync_section_to_gdrive(user.id, "finance", db)
