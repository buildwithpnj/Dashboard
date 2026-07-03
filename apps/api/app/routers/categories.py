from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import DB, CurrentUser
from app.models.finance import Category
from app.schemas.finance import CategoryCreate, CategoryKind, CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(user: CurrentUser, db: DB):
    result = await db.execute(
        select(Category)
        .where(Category.user_id == user.id, Category.parent_id.is_(None))
        .options(selectinload(Category.children))
        .order_by(Category.name)
    )
    categories = result.scalars().all()
    return categories


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(body: CategoryCreate, user: CurrentUser, db: DB):
    # If parent_id given, verify it belongs to user
    if body.parent_id:
        result = await db.execute(
            select(Category).where(
                Category.id == body.parent_id, Category.user_id == user.id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found"
            )

    category = Category(
        name=body.name,
        parent_id=body.parent_id,
        kind=body.kind.value,
        user_id=user.id,
    )
    db.add(category)
    await db.flush()
    await db.refresh(category)

    return CategoryResponse(
        id=category.id,
        name=category.name,
        parent_id=category.parent_id,
        kind=CategoryKind(category.kind),
        children=[],
    )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str, user: CurrentUser, db: DB):
    result = await db.execute(
        select(Category).where(Category.id == category_id, Category.user_id == user.id)
    )
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )

    await db.delete(category)
