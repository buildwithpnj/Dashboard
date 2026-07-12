from sqlalchemy import String, Integer, Float, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, UUIDMixin

class AccessRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "access_requests"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(1024), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending, approved, rejected

class PreviewSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "durable_preview_sessions"

    ip_address: Mapped[str] = mapped_column(String(255), nullable=False)
    turns: Mapped[int] = mapped_column(Integer, default=0)
    tokens: Mapped[int] = mapped_column(Integer, default=0)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class SystemConfig(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "system_configs"

    key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    value: Mapped[str] = mapped_column(String(2048), nullable=False)

class AdminAuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "admin_audit_logs"

    admin_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=True)
