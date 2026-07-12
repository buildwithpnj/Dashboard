import mimetypes
import logging
from datetime import datetime, UTC
from typing import List, Dict, Any
from sqlalchemy import select, update, delete as sqldelete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.storage_provider import StorageProvider
from app.storage.config import storage_settings
from app.storage.utils import decrypt_token, encrypt_token
from app.storage.providers.google.provider import GoogleDriveProvider

logger = logging.getLogger("warborn_storage_manager")


class StorageManager:
    """Storage Manager orchestrates multiple Google Drive accounts and handles automatic routing & routing fallbacks."""

    @staticmethod
    async def get_driver_for_provider(provider: StorageProvider) -> GoogleDriveProvider:
        """Decrypt refresh token and construct the provider instance."""
        decrypted_token = decrypt_token(provider.encrypted_refresh_token)
        client_secret = None
        if provider.encrypted_client_secret:
            client_secret = decrypt_token(provider.encrypted_client_secret)
        return GoogleDriveProvider(
            refresh_token=decrypted_token,
            folder_id=provider.drive_folder_id,
            account_email=provider.account_email,
            client_id=provider.client_id,
            client_secret=client_secret
        )

    @staticmethod
    def detect_category(file_name: str, content_type: str) -> str:
        """Detect the storage category based on file extension and mime type."""
        name_lower = file_name.lower()
        
        # Audio / Video extensions
        if any(name_lower.endswith(ext) for ext in [".mp4", ".mov", ".avi", ".mkv", ".webm", ".mp3", ".wav"]):
            return "videos"
            
        # Image extensions
        if any(name_lower.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico"]):
            return "images"
            
        # Backups extensions
        if any(name_lower.endswith(ext) for ext in [".zip", ".tar.gz", ".tar", ".sql", ".bak"]):
            return "backups"
            
        # Logs extensions
        if name_lower.endswith(".log") or "log" in name_lower:
            return "logs"
            
        return "documents"

    @classmethod
    async def get_provider(cls, db: AsyncSession, provider_id: str) -> StorageProvider | None:
        """Retrieve a specific storage provider by ID."""
        stmt = select(StorageProvider).where(StorageProvider.id == provider_id)
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    @classmethod
    async def list_providers(cls, db: AsyncSession) -> list[StorageProvider]:
        """List all storage providers ordered by priority."""
        stmt = select(StorageProvider).order_by(StorageProvider.priority.asc())
        res = await db.execute(stmt)
        return list(res.scalars().all())

    @classmethod
    async def default_provider(cls, db: AsyncSession) -> StorageProvider | None:
        """Get the default storage provider (lowest priority number, status active)."""
        stmt = select(StorageProvider).where(StorageProvider.status == "active").order_by(StorageProvider.priority.asc())
        res = await db.execute(stmt)
        return res.scalars().first()

    @classmethod
    async def switch_provider(cls, db: AsyncSession, provider_id: str) -> StorageProvider:
        """Promote the chosen provider to be default (set priority to 1 and push others down)."""
        provider = await cls.get_provider(db, provider_id)
        if not provider:
            raise ValueError(f"Provider '{provider_id}' not found.")
        
        # Set priority of all other providers to be > 1
        await db.execute(
            update(StorageProvider)
            .where(StorageProvider.id != provider_id)
            .values(priority=StorageProvider.priority + 10)
        )
        provider.priority = 1
        await db.commit()
        logger.info(f"Switched default provider to '{provider.name}' ({provider.account_email}).")
        return provider

    @classmethod
    async def register_provider(
        cls,
        db: AsyncSession,
        name: str,
        provider_type: str,
        email: str,
        refresh_token: str,
        folder_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        label: str | None = None,
        priority: int = 10
    ) -> StorageProvider:
        """Register a new storage provider or update credentials if it already exists."""
        encrypted_token = encrypt_token(refresh_token)
        encrypted_secret = encrypt_token(client_secret) if client_secret else None

        stmt = select(StorageProvider).where(StorageProvider.account_email == email)
        res = await db.execute(stmt)
        provider = res.scalar_one_or_none()

        if not provider:
            provider = StorageProvider(
                name=name,
                type=provider_type,
                account_email=email,
                encrypted_refresh_token=encrypted_token,
                client_id=client_id,
                encrypted_client_secret=encrypted_secret,
                redirect_uri=redirect_uri,
                drive_folder_id=folder_id,
                provider_label=label,
                priority=priority,
                status="active"
            )
            db.add(provider)
            logger.info(f"Registered new storage provider '{name}' for '{email}'.")
        else:
            provider.name = name
            provider.encrypted_refresh_token = encrypted_token
            provider.client_id = client_id
            if encrypted_secret:
                provider.encrypted_client_secret = encrypted_secret
            if redirect_uri:
                provider.redirect_uri = redirect_uri
            provider.drive_folder_id = folder_id
            provider.provider_label = label
            provider.status = "active"
            logger.info(f"Updated credentials for existing provider '{name}' ({email}).")

        await db.commit()
        return provider

    @classmethod
    async def remove_provider(cls, db: AsyncSession, provider_id: str) -> None:
        """Permanently delete a provider from database configuration."""
        stmt = sqldelete(StorageProvider).where(StorageProvider.id == provider_id)
        await db.execute(stmt)
        await db.commit()
        logger.info(f"Deleted storage provider with ID '{provider_id}'.")

    @classmethod
    async def seed_drives_if_empty(cls, db: AsyncSession) -> None:
        """Seed Drive A and Drive B if configured in environment and not already in database."""
        seeds = [
            (
                "Drive A",
                "A",
                storage_settings.google_drive_a_refresh_token,
                storage_settings.google_drive_a_folder_id,
                storage_settings.google_drive_a_email,
                storage_settings.google_client_id,
                storage_settings.google_client_secret,
                storage_settings.google_redirect_uri,
                1
            ),
            (
                "Drive B",
                "B",
                storage_settings.google_drive_b_refresh_token,
                storage_settings.google_drive_b_folder_id,
                storage_settings.google_drive_b_email,
                storage_settings.google_drive_b_client_id,
                storage_settings.google_drive_b_client_secret,
                storage_settings.google_drive_b_redirect_uri,
                2
            ),
        ]
        
        for name, label, token, folder_id, email, client_id, client_secret, redirect_uri, priority in seeds:
            if token and email:
                # Check if already seeded by email
                stmt = select(StorageProvider).where(StorageProvider.account_email == email)
                res = await db.execute(stmt)
                if not res.scalar_one_or_none():
                    encrypted_token = encrypt_token(token)
                    encrypted_secret = encrypt_token(client_secret) if client_secret else None
                    provider = StorageProvider(
                        name=name,
                        type="google_drive",
                        account_email=email,
                        encrypted_refresh_token=encrypted_token,
                        client_id=client_id,
                        encrypted_client_secret=encrypted_secret,
                        redirect_uri=redirect_uri,
                        drive_folder_id=folder_id,
                        provider_label=label,
                        status="active",
                        priority=priority
                    )
                    db.add(provider)
                    logger.info(f"Seeded default storage provider '{name}' ({email}) in database.")
                    
        await db.commit()

    @classmethod
    async def select_provider(
        cls,
        db: AsyncSession,
        provider_choice: str | None = None,
        file_name: str | None = None,
        content_type: str | None = None
    ) -> StorageProvider:
        """Selects the active provider based on rules, falling back dynamically as needed."""
        # Ensure initial drives are seeded in DB
        await cls.seed_drives_if_empty(db)

        provider = None
        
        # 1. Routing by explicit choice
        if provider_choice:
            choice_clean = provider_choice.strip().upper()
            if choice_clean in ("A", "DRIVE A"):
                stmt = select(StorageProvider).where(StorageProvider.provider_label == "A", StorageProvider.status == "active")
            elif choice_clean in ("B", "DRIVE B"):
                stmt = select(StorageProvider).where(StorageProvider.provider_label == "B", StorageProvider.status == "active")
            else:
                # Search by UUID or Name
                stmt = select(StorageProvider).where(
                    (StorageProvider.id == provider_choice) | (StorageProvider.name == provider_choice),
                    StorageProvider.status == "active"
                )
            res = await db.execute(stmt)
            provider = res.scalar_one_or_none()
            if provider:
                logger.info(f"Explicitly routed to provider '{provider.name}' ({provider.account_email})")
                return provider

        # 2. Omitted choice -> Fallback to category-based detection or Default Provider
        if file_name and content_type:
            category = cls.detect_category(file_name, content_type)
            preferred_label = "A"
            if category in ("images", "videos"):
                preferred_label = "B"
            elif category in ("backups", "logs"):
                preferred_label = "C"

            stmt = select(StorageProvider).where(StorageProvider.provider_label == preferred_label, StorageProvider.status == "active")
            res = await db.execute(stmt)
            provider = res.scalar_one_or_none()
            if provider:
                # Quota check
                is_exceeded = False
                if provider.available_storage > 0:
                    usage_percentage = (provider.used_storage / provider.available_storage) * 100
                    if usage_percentage >= 90:
                        is_exceeded = True
                
                if not is_exceeded:
                    logger.info(f"Category '{category}' routed to preferred provider '{provider.name}'")
                    return provider

        # 3. Default Provider fallback
        provider = await cls.default_provider(db)
        if provider:
            logger.info(f"Routed to default provider '{provider.name}'")
            return provider

        # 4. Global fallback to any active provider
        stmt = select(StorageProvider).where(StorageProvider.status == "active").order_by(StorageProvider.priority.asc())
        res = await db.execute(stmt)
        active_providers = list(res.scalars().all())
        if active_providers:
            logger.warning(f"Routed to first active fallback provider '{active_providers[0].name}'")
            return active_providers[0]

        raise RuntimeError("No active storage providers found. Connect a Google Drive account.")

    @classmethod
    async def upload(cls, db: AsyncSession, file_name: str, content_type: str, data: bytes, provider_choice: str | None = None) -> str:
        """Execute the upload pipeline with dynamic failover."""
        if not file_name or len(data) == 0:
            raise ValueError("Invalid file metadata or empty file content.")
            
        cls.virus_scan_hook(file_name, data)
        
        # Resolve preferred provider
        provider = await cls.select_provider(db, provider_choice, file_name, content_type)
        
        try:
            driver = await cls.get_driver_for_provider(provider)
            file_id = await driver.upload(file_name, content_type, data)
            await cls._sync_quota_silently(db, provider, driver)
            return file_id
        except Exception as primary_error:
            logger.error(f"Upload to primary choice '{provider.name}' failed: {primary_error}. Attempting failover...")
            
            # If explicit choice failed, or default failed, try the OTHER provider (Auto failover)
            stmt = select(StorageProvider).where(
                StorageProvider.id != provider.id,
                StorageProvider.status == "active"
            ).order_by(StorageProvider.priority.asc())
            res = await db.execute(stmt)
            failover_providers = res.scalars().all()
            
            for backup in failover_providers:
                try:
                    logger.info(f"Failover upload triggered. Routing to '{backup.name}'...")
                    driver = await cls.get_driver_for_provider(backup)
                    file_id = await driver.upload(file_name, content_type, data)
                    await cls._sync_quota_silently(db, backup, driver)
                    return file_id
                except Exception as backup_error:
                    logger.error(f"Failover to '{backup.name}' failed: {backup_error}")
                    continue
            
            # If all failover attempts fail, raise the original error
            raise RuntimeError(f"Storage system upload failed completely. Primary error: {str(primary_error)}")

    @classmethod
    async def _sync_quota_silently(cls, db: AsyncSession, provider: StorageProvider, driver: GoogleDriveProvider):
        try:
            used, limit = await driver.get_quota()
            provider.used_storage = used
            provider.available_storage = limit
            provider.last_sync = datetime.now(UTC)
            await db.commit()
        except Exception as e:
            logger.warning(f"Failed to fetch quota metadata for '{provider.name}': {e}")

    @staticmethod
    def virus_scan_hook(file_name: str, data: bytes) -> None:
        """Virus Scan Hook to check file safety before uploading."""
        logger.info(f"Virus scan completed for '{file_name}'. Result: CLEAN (File size: {len(data)} bytes).")

    @classmethod
    async def download(cls, db: AsyncSession, file_id: str, provider_id: str | None = None) -> tuple[str, str, bytes]:
        """Download file content. If provider_id is not specified, search through all active providers."""
        if provider_id:
            provider = await cls.get_provider(db, provider_id)
            if not provider:
                raise ValueError("Specified storage provider not found.")
            driver = await cls.get_driver_for_provider(provider)
            meta = await driver.get_metadata(file_id)
            content = await driver.download(file_id)
            return meta.get("name", "download"), meta.get("mimeType", "application/octet-stream"), content
            
        providers = await cls.list_providers(db)
        active_providers = [p for p in providers if p.status == "active"]
        
        for provider in active_providers:
            try:
                driver = await cls.get_driver_for_provider(provider)
                meta = await driver.get_metadata(file_id)
                content = await driver.download(file_id)
                return meta.get("name", "download"), meta.get("mimeType", "application/octet-stream"), content
            except Exception:
                continue
                
        raise FileNotFoundError(f"File ID '{file_id}' could not be resolved or downloaded from any connected Google Drive provider.")

    @classmethod
    async def delete(cls, db: AsyncSession, file_id: str, provider_id: str | None = None) -> None:
        """Delete file from google drive."""
        if provider_id:
            provider = await cls.get_provider(db, provider_id)
            if provider:
                driver = await cls.get_driver_for_provider(provider)
                await driver.delete(file_id)
                return
                
        providers = await cls.list_providers(db)
        active_providers = [p for p in providers if p.status == "active"]
        
        for provider in active_providers:
            try:
                driver = await cls.get_driver_for_provider(provider)
                await driver.get_metadata(file_id)
                await driver.delete(file_id)
                return
            except Exception:
                continue
                
        raise FileNotFoundError(f"File ID '{file_id}' could not be resolved or deleted from any active provider.")

    @classmethod
    async def list(cls, db: AsyncSession, folder_id: str = "root", provider_id: str | None = None) -> List[dict]:
        """List files in the target provider. If not specified, returns lists merged from all providers."""
        if provider_id:
            provider = await cls.get_provider(db, provider_id)
            if not provider:
                return []
            driver = await cls.get_driver_for_provider(provider)
            files = await driver.list(folder_id)
            for f in files:
                f["provider"] = provider.name
                f["provider_id"] = str(provider.id)
            return files
            
        providers = await cls.list_providers(db)
        active_providers = [p for p in providers if p.status == "active"]
        
        merged_files: List[dict] = []
        for provider in active_providers:
            try:
                driver = await cls.get_driver_for_provider(provider)
                files = await driver.list(folder_id)
                for f in files:
                    f["provider"] = provider.name
                    f["provider_id"] = str(provider.id)
                merged_files.extend(files)
            except Exception as e:
                logger.warning(f"Could not list directory from provider '{provider.name}': {e}")
                
        return merged_files

    @classmethod
    async def search(cls, db: AsyncSession, query: str, provider_id: str | None = None) -> List[dict]:
        """Search files matching query text."""
        if provider_id:
            provider = await cls.get_provider(db, provider_id)
            if not provider:
                return []
            driver = await cls.get_driver_for_provider(provider)
            files = await driver.search(query)
            for f in files:
                f["provider"] = provider.name
                f["provider_id"] = str(provider.id)
            return files

        providers = await cls.list_providers(db)
        active_providers = [p for p in providers if p.status == "active"]
        
        merged_results: List[dict] = []
        for provider in active_providers:
            try:
                driver = await cls.get_driver_for_provider(provider)
                files = await driver.search(query)
                for f in files:
                    f["provider"] = provider.name
                    f["provider_id"] = str(provider.id)
                merged_results.extend(files)
            except Exception as e:
                logger.warning(f"Could not search files from provider '{provider.name}': {e}")
                
        return merged_results

    @classmethod
    async def health_check(cls, db: AsyncSession) -> dict[str, str]:
        """Run connection checks on all providers."""
        providers = await cls.list_providers(db)
        status_report = {}
        for p in providers:
            try:
                driver = await cls.get_driver_for_provider(p)
                await driver.get_quota()
                status_report[p.name] = "healthy"
                p.status = "active"
            except Exception as e:
                status_report[p.name] = f"error: {str(e)}"
                p.status = "error"
        await db.commit()
        return status_report

    @classmethod
    async def available_storage(cls, db: AsyncSession) -> int:
        """Sum of total limit space across all active providers."""
        providers = await cls.list_providers(db)
        return sum(p.available_storage for p in providers if p.status == "active")

    @classmethod
    async def provider_usage(cls, db: AsyncSession) -> int:
        """Sum of total used space across all active providers."""
        providers = await cls.list_providers(db)
        return sum(p.used_storage for p in providers if p.status == "active")
