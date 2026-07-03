from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ToolSchema(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tool_schemas"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    fields_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    records: Mapped[list["ToolRecord"]] = relationship(
        back_populates="schema", cascade="all, delete-orphan"
    )
    automations: Mapped[list["Automation"]] = relationship(
        back_populates="schema", cascade="all, delete-orphan"
    )


class ToolRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tool_records"

    tool_schema_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tool_schemas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    data_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    schema: Mapped["ToolSchema"] = relationship(back_populates="records")


class Automation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "automations"

    tool_schema_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tool_schemas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trigger_json: Mapped[str] = mapped_column(Text, nullable=False)
    action_json: Mapped[str] = mapped_column(Text, nullable=False)

    schema: Mapped["ToolSchema"] = relationship(back_populates="automations")
