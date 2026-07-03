"""initial schema

Revision ID: 001_initial
Revises: None
Create Date: 2026-07-03
"""
from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Enum types
account_type = sa.Enum("bank", "cash", "card", "investment", name="account_type")
category_kind = sa.Enum("expense", "income", name="category_kind")
transaction_source = sa.Enum("manual", "agent", name="transaction_source")
budget_period = sa.Enum("monthly", "weekly", "yearly", name="budget_period")
book_status = sa.Enum("to-read", "reading", "finished", "DNF", name="book_status")
habit_cadence = sa.Enum("daily", "weekly", "monthly", name="habit_cadence")
staging_status = sa.Enum("pending", "approved", "rejected", name="staging_status")


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ─── Users ─────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Accounts ──────────────────────────────────────────
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", account_type, nullable=False, server_default="bank"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column(
            "opening_balance", sa.Numeric(precision=15, scale=2), nullable=False, server_default="0"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Categories ────────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "parent_id",
            sa.String(36),
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("kind", category_kind, nullable=False, server_default="expense"),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )

    # ─── Transactions ──────────────────────────────────────
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "account_id",
            sa.String(36),
            sa.ForeignKey("accounts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("amount", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="INR"),
        sa.Column(
            "category_id",
            sa.String(36),
            sa.ForeignKey("categories.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("merchant", sa.String(255), nullable=False, server_default=""),
        sa.Column("note", sa.Text, nullable=False, server_default=""),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
        sa.Column("source", transaction_source, nullable=False, server_default="manual"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Budgets ───────────────────────────────────────────
    op.create_table(
        "budgets",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "category_id",
            sa.String(36),
            sa.ForeignKey("categories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("period", budget_period, nullable=False, server_default="monthly"),
        sa.Column("amount_limit", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Books ─────────────────────────────────────────────
    op.create_table(
        "books",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("status", book_status, nullable=False, server_default="to-read"),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cover_url", sa.String(1024), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Highlights ────────────────────────────────────────
    op.create_table(
        "highlights",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "book_id",
            sa.String(36),
            sa.ForeignKey("books.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("location", sa.String(50), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Habits ────────────────────────────────────────────
    op.create_table(
        "habits",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("cadence", habit_cadence, nullable=False, server_default="daily"),
        sa.Column("target", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Habit Logs ────────────────────────────────────────
    op.create_table(
        "habit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "habit_id",
            sa.String(36),
            sa.ForeignKey("habits.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("date", sa.Date(), nullable=False, index=True),
        sa.Column("value", sa.Numeric(precision=10, scale=2), nullable=False, server_default="1.0"),
    )

    # ─── Journal Entries ───────────────────────────────────
    op.create_table(
        "journal_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("body_json", sa.Text(), nullable=False),
        sa.Column("mood", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
            index=True,
        ),
    )

    # ─── Notes ─────────────────────────────────────────────
    op.create_table(
        "notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(255), nullable=False, server_default="Untitled"),
        sa.Column("body_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Note Links ────────────────────────────────────────
    op.create_table(
        "note_links",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "from_note_id",
            sa.String(36),
            sa.ForeignKey("notes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "to_note_id",
            sa.String(36),
            sa.ForeignKey("notes.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )

    # ─── Embeddings ────────────────────────────────────────
    op.create_table(
        "embeddings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=False, index=True),
        sa.Column("vector", Vector(1024), nullable=False),
    )

    # ─── Tool Schemas ──────────────────────────────────────
    op.create_table(
        "tool_schemas",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("fields_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Tool Records ──────────────────────────────────────
    op.create_table(
        "tool_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tool_schema_id",
            sa.String(36),
            sa.ForeignKey("tool_schemas.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("data_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Automations ───────────────────────────────────────
    op.create_table(
        "automations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "tool_schema_id",
            sa.String(36),
            sa.ForeignKey("tool_schemas.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("trigger_json", sa.Text(), nullable=False),
        sa.Column("action_json", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    # ─── Staging Entries ───────────────────────────────────
    op.create_table(
        "staging_entries",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("target_table", sa.String(100), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("source_doc", sa.String(500), nullable=True),
        sa.Column("status", staging_status, nullable=False, server_default="pending", index=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("staging_entries")
    op.drop_table("automations")
    op.drop_table("tool_records")
    op.drop_table("tool_schemas")
    op.drop_table("embeddings")
    op.drop_table("note_links")
    op.drop_table("notes")
    op.drop_table("journal_entries")
    op.drop_table("habit_logs")
    op.drop_table("habits")
    op.drop_table("highlights")
    op.drop_table("books")
    op.drop_table("budgets")
    op.drop_table("transactions")
    op.drop_table("categories")
    op.drop_table("accounts")
    op.drop_table("users")

    # Drop enum types
    staging_status.drop(op.get_bind(), checkfirst=True)
    habit_cadence.drop(op.get_bind(), checkfirst=True)
    book_status.drop(op.get_bind(), checkfirst=True)
    budget_period.drop(op.get_bind(), checkfirst=True)
    transaction_source.drop(op.get_bind(), checkfirst=True)
    category_kind.drop(op.get_bind(), checkfirst=True)
    account_type.drop(op.get_bind(), checkfirst=True)

    # Drop extension
    op.execute("DROP EXTENSION IF EXISTS vector")
