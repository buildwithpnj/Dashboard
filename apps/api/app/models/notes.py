from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Note(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notes"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, default="Untitled")
    body_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # comma separated


class NoteLink(Base, UUIDMixin):
    __tablename__ = "note_links"

    from_note_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    to_note_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True
    )


class Embedding(Base, UUIDMixin):
    __tablename__ = "embeddings"

    # e.g., 'note', 'book', 'transaction'
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    # BGE-M3 vectors are 1024 dimensions
    vector: Mapped[list[float]] = mapped_column(Vector(1024), nullable=False)
