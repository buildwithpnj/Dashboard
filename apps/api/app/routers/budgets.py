from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import DB, CurrentUser
from app.gdrive_sync import sync_section_to_gdrive
from app.models.finance import Budget, Category
from app.schemas.finance import BudgetCreate, BudgetPeriod, BudgetResponse, BudgetUpdate

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetResponse])
async def list_budgets(user: CurrentUser, db: DB):
    result = await db.execute(
        select(Budget).where(Budget.user_id == user.id).order_by(Budget.created_at.desc())
    )
    budgets = result.scalars().all()

    responses = []
    for b in budgets:
        cat_result = await db.execute(select(Category).where(Category.id == b.category_id))
        cat = cat_result.scalar_one_or_none()
        responses.append(
            BudgetResponse(
                id=b.id,
                category_id=b.category_id,
                category_name=cat.name if cat else None,
                period=BudgetPeriod(b.period),
                amount_limit=float(b.amount_limit),
                spent=0,  # TODO: compute from transactions
            )
        )
    return responses


@router.post("", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(body: BudgetCreate, user: CurrentUser, db: DB):
    # Verify category belongs to user
    result = await db.execute(
        select(Category).where(Category.id == body.category_id, Category.user_id == user.id)
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    budget = Budget(
        user_id=user.id,
        category_id=body.category_id,
        period=body.period.value,
        amount_limit=body.amount_limit,
    )
    db.add(budget)
    await db.flush()
    await db.refresh(budget)
    await sync_section_to_gdrive(user.id, "finance", db)

    return BudgetResponse(
        id=budget.id,
        category_id=budget.category_id,
        category_name=cat.name,
        period=BudgetPeriod(budget.period),
        amount_limit=float(budget.amount_limit),
        spent=0,
    )


@router.patch("/{budget_id}", response_model=BudgetResponse)
async def update_budget(budget_id: str, body: BudgetUpdate, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == user.id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(budget, field, value)

    await db.flush()
    await db.refresh(budget)
    await sync_section_to_gdrive(user.id, "finance", db)

    cat_result = await db.execute(select(Category).where(Category.id == budget.category_id))
    cat = cat_result.scalar_one_or_none()

    return BudgetResponse(
        id=budget.id,
        category_id=budget.category_id,
        category_name=cat.name if cat else None,
        period=BudgetPeriod(budget.period),
        amount_limit=float(budget.amount_limit),
        spent=0,
    )


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(budget_id: str, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Budget).where(Budget.id == budget_id, Budget.user_id == user.id)
    )
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")

    await db.delete(budget)
    await sync_section_to_gdrive(user.id, "finance", db)
