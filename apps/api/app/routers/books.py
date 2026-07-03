from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.deps import DB, CurrentUser
from app.gdrive_sync import sync_section_to_gdrive
from app.models.books import Book, Highlight

router = APIRouter(prefix="/api/books", tags=["Books"])


class BookUpdate(BaseModel):
    title: str
    author: str
    status: str
    rating: int | None = None
    cover_url: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class HighlightCreate(BaseModel):
    text: str
    location: str | None = None
    tags: str | None = None


@router.get("")
async def list_books(current_user: CurrentUser, db: DB, q: str | None = None):
    query = select(Book).where(Book.user_id == current_user.id)
    if q:
        query = query.where(
            Book.title.ilike(f"%{q}%") | Book.author.ilike(f"%{q}%")
        )
    query = query.order_by(Book.updated_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_book(current_user: CurrentUser, db: DB):
    book = Book(
        user_id=current_user.id,
        title="Untitled Book",
        author="Unknown Author",
        status="to-read",
        rating=None,
        cover_url=None,
    )
    db.add(book)
    await db.flush()
    await db.refresh(book)
    await sync_section_to_gdrive(current_user.id, "books", db)
    return book


@router.get("/{book_id}")
async def get_book(book_id: str, current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Book).where(Book.id == book_id, Book.user_id == current_user.id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    hl_result = await db.execute(
        select(Highlight)
        .where(Highlight.book_id == book_id)
        .order_by(Highlight.created_at.desc())
    )
    highlights = hl_result.scalars().all()

    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "status": book.status,
        "rating": book.rating,
        "started_at": book.started_at,
        "finished_at": book.finished_at,
        "cover_url": book.cover_url,
        "created_at": book.created_at,
        "updated_at": book.updated_at,
        "highlights": highlights,
    }


@router.put("/{book_id}")
async def update_book(
    book_id: str, body: BookUpdate, current_user: CurrentUser, db: DB
):
    result = await db.execute(
        select(Book).where(Book.id == book_id, Book.user_id == current_user.id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.title = body.title
    book.author = body.author
    book.status = body.status
    book.rating = body.rating
    book.cover_url = body.cover_url
    book.started_at = body.started_at
    book.finished_at = body.finished_at

    await db.flush()
    await db.refresh(book)
    await sync_section_to_gdrive(current_user.id, "books", db)
    return book


@router.delete("/{book_id}")
async def delete_book(book_id: str, current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(Book).where(Book.id == book_id, Book.user_id == current_user.id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    await db.delete(book)
    await sync_section_to_gdrive(current_user.id, "books", db)
    return {"status": "success"}


@router.post("/{book_id}/highlights", status_code=status.HTTP_201_CREATED)
async def create_highlight(
    book_id: str, body: HighlightCreate, current_user: CurrentUser, db: DB
):
    result = await db.execute(
        select(Book).where(Book.id == book_id, Book.user_id == current_user.id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    highlight = Highlight(
        book_id=book_id,
        text=body.text,
        location=body.location,
        tags=body.tags,
    )
    db.add(highlight)
    await db.flush()
    await db.refresh(highlight)
    await sync_section_to_gdrive(current_user.id, "books", db)
    return highlight


@router.delete("/highlights/{highlight_id}")
async def delete_highlight(
    highlight_id: str, current_user: CurrentUser, db: DB
):
    hl_result = await db.execute(
        select(Highlight)
        .join(Book, Highlight.book_id == Book.id)
        .where(Highlight.id == highlight_id, Book.user_id == current_user.id)
    )
    highlight = hl_result.scalar_one_or_none()
    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found")

    await db.delete(highlight)
    await sync_section_to_gdrive(current_user.id, "books", db)
    return {"status": "success"}
