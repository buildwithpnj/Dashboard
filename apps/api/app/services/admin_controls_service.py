from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.governance import SystemConfig, AdminAuditLog
from typing import Dict, Any, List, Optional

class AdminControlsService:
    @classmethod
    async def get_config(cls, db: AsyncSession, key: str, default: str) -> str:
        result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
        cfg = result.scalar_one_or_none()
        return cfg.value if cfg else default

    @classmethod
    async def set_config(cls, db: AsyncSession, admin_id: str, key: str, value: str):
        result = await db.execute(select(SystemConfig).where(SystemConfig.key == key))
        cfg = result.scalar_one_or_none()
        if cfg:
            cfg.value = value
        else:
            cfg = SystemConfig(key=key, value=value)
            db.add(cfg)
            
        # Log admin audit trail
        log = AdminAuditLog(
            admin_id=admin_id,
            action="update_system_config",
            details=f"Updated config key={key} to value={value}"
        )
        db.add(log)
        await db.commit()

    @classmethod
    async def is_preview_disabled(cls, db: AsyncSession) -> bool:
        val = await cls.get_config(db, "disable_preview_globally", "false")
        return val.lower() == "true"

    @classmethod
    async def get_disabled_intents(cls, db: AsyncSession) -> List[str]:
        val = await cls.get_config(db, "disabled_intents", "")
        return [i.strip() for i in val.split(",") if i.strip()]

    @classmethod
    async def list_audit_logs(cls, db: AsyncSession) -> List[AdminAuditLog]:
        result = await db.execute(select(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()))
        return list(result.scalars().all())
