from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Habit(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "habits"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cadence: Mapped[str] = mapped_column(
        Enum("daily", "weekly", "monthly", name="habit_cadence"),
        nullable=False,
        default="daily",
    )
    target: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    logs: Mapped[list["HabitLog"]] = relationship(
        back_populates="habit", cascade="all, delete-orphan"
    )


class HabitLog(Base, UUIDMixin):
    __tablename__ = "habit_logs"

    habit_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    value: Mapped[float] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, default=1.0
    )

    habit: Mapped["Habit"] = relationship(back_populates="logs")


class JournalEntry(Base, UUIDMixin):
    __tablename__ = "journal_entries"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    body_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON structure
    mood: Mapped[int | None] = mapped_column(Integer, nullable=True)  # e.g., 1 to 5 scale
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
