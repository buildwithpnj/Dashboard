from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Book(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "books"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("to-read", "reading", "finished", "DNF", name="book_status"),
        nullable=False,
        default="to-read",
    )
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    highlights: Mapped[list["Highlight"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )


class Highlight(Base, UUIDMixin):
    __tablename__ = "highlights"

    book_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # Storing tags as simple comma-separated string
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    book: Mapped["Book"] = relationship(back_populates="highlights")
