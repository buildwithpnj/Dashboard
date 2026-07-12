import logging
from typing import Any
from fastapi import APIRouter, File, HTTPException, UploadFile, Query, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy import select
from pydantic import BaseModel

from app.deps import DB, CurrentUser
from app.models.storage_provider import StorageProvider
from app.storage.services import StorageManager
from app.storage.providers.google.oauth import GoogleOAuthManager
from app.storage.utils import encrypt_token
from app.storage.config import storage_settings

logger = logging.getLogger("warborn_storage_routes")

router = APIRouter(prefix="/api/storage", tags=["Storage Management"])


class CallbackRequest(BaseModel):
    code: str


# ── Provider A OAuth ──────────────────────────────────────────────────────────

@router.get("/auth/google/login")
async def google_auth_login(current_user: CurrentUser):
    """Generate authorization consent URL to connect Google Drive Provider A (Primary)."""
    oauth = GoogleOAuthManager(
        client_id=storage_settings.google_client_id,
        client_secret=storage_settings.google_client_secret,
        redirect_uri=storage_settings.google_redirect_uri
    )
    try:
        url = oauth.get_authorization_url()
        return {"url": url}
    except Exception as e:
        logger.error(f"Failed to generate google consent url for Provider A: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/google/callback")
async def google_auth_callback(body: CallbackRequest, current_user: CurrentUser, db: DB):
    """Receive code from consent flow, exchange for tokens, and register Provider A."""
    oauth = GoogleOAuthManager(
        client_id=storage_settings.google_client_id,
        client_secret=storage_settings.google_client_secret,
        redirect_uri=storage_settings.google_redirect_uri
    )
    try:
        tokens = oauth.exchange_code_for_tokens(body.code)
        refresh_token = tokens.get("refresh_token")
        email = tokens.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google OAuth did not return an account email.")

        if not refresh_token:
            stmt = select(StorageProvider).where(StorageProvider.account_email == email)
            res = await db.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                return {"status": "success", "message": f"Provider A for '{email}' is already fully authorized."}
                
            raise HTTPException(
                status_code=400,
                detail="Google did not return a refresh token. Please reset permissions in your Google Account and try again."
            )

        provider = await StorageManager.register_provider(
            db=db,
            name="Drive A",
            provider_type="google_drive",
            email=email,
            refresh_token=refresh_token,
            folder_id=storage_settings.google_drive_a_folder_id,
            client_id=storage_settings.google_client_id,
            client_secret=storage_settings.google_client_secret,
            redirect_uri=storage_settings.google_redirect_uri,
            label="A",
            priority=1
        )
        return {"status": "success", "connected": True, "email": email, "provider": provider.name}

    except Exception as e:
        logger.error(f"Failed to handle oauth callback for Provider A: {e}")
        raise HTTPException(status_code=400, detail=f"OAuth connection failed: {str(e)}")


# ── Provider B OAuth ──────────────────────────────────────────────────────────

@router.get("/auth/google/provider-b/login")
async def google_auth_provider_b_login(current_user: CurrentUser):
    """Generate authorization consent URL to connect Google Drive Provider B."""
    oauth = GoogleOAuthManager(
        client_id=storage_settings.google_drive_b_client_id,
        client_secret=storage_settings.google_drive_b_client_secret,
        redirect_uri=storage_settings.google_drive_b_redirect_uri
    )
    try:
        url = oauth.get_authorization_url()
        return {"url": url}
    except Exception as e:
        logger.error(f"Failed to generate google consent url for Provider B: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/google/provider-b/callback")
async def google_auth_provider_b_callback(body: CallbackRequest, current_user: CurrentUser, db: DB):
    """Receive code from consent flow, exchange for tokens, and register Provider B."""
    oauth = GoogleOAuthManager(
        client_id=storage_settings.google_drive_b_client_id,
        client_secret=storage_settings.google_drive_b_client_secret,
        redirect_uri=storage_settings.google_drive_b_redirect_uri
    )
    try:
        tokens = oauth.exchange_code_for_tokens(body.code)
        refresh_token = tokens.get("refresh_token")
        email = tokens.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google OAuth did not return an account email for Provider B.")

        if not refresh_token:
            stmt = select(StorageProvider).where(StorageProvider.account_email == email)
            res = await db.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                return {"status": "success", "message": f"Provider B for '{email}' is already fully authorized."}
                
            raise HTTPException(
                status_code=400,
                detail="Google did not return a refresh token for Provider B. Please reset permissions in your Google Account and try again."
            )

        provider = await StorageManager.register_provider(
            db=db,
            name="Drive B",
            provider_type="google_drive",
            email=email,
            refresh_token=refresh_token,
            folder_id=storage_settings.google_drive_b_folder_id,
            client_id=storage_settings.google_drive_b_client_id,
            client_secret=storage_settings.google_drive_b_client_secret,
            redirect_uri=storage_settings.google_drive_b_redirect_uri,
            label="B",
            priority=2
        )
        return {"status": "success", "connected": True, "email": email, "provider": provider.name}

    except Exception as e:
        logger.error(f"Failed to handle oauth callback for Provider B: {e}")
        raise HTTPException(status_code=400, detail=f"OAuth connection failed: {str(e)}")


# ── File Access Routing ───────────────────────────────────────────────────────

@router.post("/upload")
async def upload_file(
    db: DB,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    provider: str | None = Query(default=None),
):
    """Upload a file. Auto-routes by category/default if provider is omitted, with dynamic failover."""
    try:
        content = await file.read()
        if not file.filename:
            raise HTTPException(status_code=400, detail="Uploaded file is missing a filename.")
        content_type = file.content_type or "application/octet-stream"
        file_id = await StorageManager.upload(
            db=db,
            file_name=file.filename,
            content_type=content_type,
            data=content,
            provider_choice=provider
        )
        return {"status": "success", "file_id": file_id, "filename": file.filename}
    except Exception as e:
        logger.error(f"File upload error in route: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: DB,
    current_user: CurrentUser,
    provider_id: str | None = Query(default=None),
):
    """Download a file. Dynamic download search through active providers if ID is omitted."""
    try:
        name, mime, content = await StorageManager.download(db, file_id, provider_id)
        from io import BytesIO
        return StreamingResponse(
            BytesIO(content),
            media_type=mime,
            headers={
                "Content-Disposition": f'attachment; filename="{name}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            }
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Download route error for file '{file_id}': {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/list")
async def list_files(
    db: DB,
    current_user: CurrentUser,
    folder_id: str = Query(default="root"),
    provider_id: str | None = Query(default=None),
):
    """List active directory files. Merges directories from all providers if ID is omitted."""
    try:
        files = await StorageManager.list(db, folder_id, provider_id)
        return {"files": files}
    except Exception as e:
        logger.error(f"List files route error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/delete/{file_id}")
async def delete_file(
    file_id: str,
    db: DB,
    current_user: CurrentUser,
    provider_id: str | None = Query(default=None),
):
    """Delete a file from the cloud storage system."""
    try:
        await StorageManager.delete(db, file_id, provider_id)
        return {"status": "success", "message": f"File '{file_id}' deleted successfully."}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Delete file route error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search")
async def search_files(
    q: str,
    db: DB,
    current_user: CurrentUser,
    provider_id: str | None = Query(default=None),
):
    """Search active files matching search token."""
    try:
        files = await StorageManager.search(db, q, provider_id)
        return {"files": files}
    except Exception as e:
        logger.error(f"Search route error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ── Provider Management ───────────────────────────────────────────────────────

@router.get("/providers")
async def get_providers(db: DB, current_user: CurrentUser):
    """List details, health, and status report for all registered storage providers."""
    await StorageManager.seed_drives_if_empty(db)
    providers = await StorageManager.list_providers(db)
    
    output = []
    for p in providers:
        output.append({
            "id": str(p.id),
            "name": p.name,
            "provider_label": p.provider_label,
            "type": p.type,
            "account_email": p.account_email,
            "drive_folder_id": p.drive_folder_id,
            "status": p.status,
            "connected": p.status == "active",
            "used_storage": p.used_storage,
            "available_storage": p.available_storage,
            "priority": p.priority,
            "last_sync": p.last_sync.isoformat() if p.last_sync else None
        })
    return {"providers": output}


@router.post("/providers/{provider_id}/set-default")
async def set_default_provider(provider_id: str, db: DB, current_user: CurrentUser):
    """Set the target provider to be default (priority = 1)."""
    try:
        provider = await StorageManager.switch_provider(db, provider_id)
        return {"status": "success", "message": f"Default provider switched to '{provider.name}'."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str, db: DB, current_user: CurrentUser):
    """Unlink/remove a registered storage provider."""
    try:
        await StorageManager.remove_provider(db, provider_id)
        return {"status": "success", "message": "Provider removed successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/health")
async def storage_health(db: DB, current_user: CurrentUser):
    """Perform real-time connectivity checks on all registered storage providers."""
    try:
        status_report = await StorageManager.health_check(db)
        is_healthy = all(val == "healthy" for val in status_report.values())
        return {
            "status": "healthy" if is_healthy else "degraded",
            "details": status_report
        }
    except Exception as e:
        logger.error(f"Health route error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
