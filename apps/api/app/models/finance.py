from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Account(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "accounts"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(
        Enum("bank", "cash", "card", "investment", name="account_type"),
        nullable=False,
        default="bank",
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    opening_balance: Mapped[float] = mapped_column(
        Numeric(precision=15, scale=2), nullable=False, default=0
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )


class Category(Base, UUIDMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )
    kind: Mapped[str] = mapped_column(
        Enum("expense", "income", name="category_kind"),
        nullable=False,
        default="expense",
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    children: Mapped[list["Category"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan"
    )
    parent: Mapped["Category | None"] = relationship(
        back_populates="children", remote_side="Category.id"
    )


class Transaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transactions"

    account_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(precision=15, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    category_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    merchant: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(
        Enum("manual", "agent", name="transaction_source"),
        nullable=False,
        default="manual",
    )

    account: Mapped["Account"] = relationship(back_populates="transactions")
    category: Mapped["Category | None"] = relationship()


class Budget(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "budgets"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    period: Mapped[str] = mapped_column(
        Enum("monthly", "weekly", "yearly", name="budget_period"),
        nullable=False,
        default="monthly",
    )
    amount_limit: Mapped[float] = mapped_column(Numeric(precision=15, scale=2), nullable=False)

    category: Mapped["Category"] = relationship()
