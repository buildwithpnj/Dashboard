from datetime import UTC, datetime
from io import BytesIO
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.deps import DB, CurrentUser
from app.models.gdrive import GoogleCredentials
from app.models.user import User

router = APIRouter(prefix="/api/gdrive", tags=["Google Drive"])


class CallbackRequest(BaseModel):
    code: str


class CreateFolderRequest(BaseModel):
    name: str
    parent_id: str | None = None


async def get_drive_service(user: User, db: AsyncSession):
    result = await db.execute(
        select(GoogleCredentials).where(GoogleCredentials.user_id == user.id)
    )
    db_creds = result.scalar_one_or_none()
    if not db_creds:
        raise HTTPException(status_code=401, detail="Google Drive is not connected.")

    creds = Credentials(
        token=db_creds.token,
        refresh_token=db_creds.refresh_token,
        token_uri=db_creds.token_uri,
        client_id=db_creds.client_id,
        client_secret=db_creds.client_secret,
        scopes=db_creds.scopes.split(","),
    )

    # Check if token is expired
    is_expired = creds.expired or (
        creds.expiry
        and creds.expiry.replace(tzinfo=None) < datetime.now(UTC).replace(tzinfo=None)
    )
    if is_expired:
        try:
            creds.refresh(Request())
            # Save updated credentials back to database
            db_creds.token = creds.token
            db_creds.expiry = creds.expiry
            await db.commit()
        except Exception as e:
            # Token refresh failed, likely revoked or expired
            await db.delete(db_creds)
            await db.commit()
            raise HTTPException(
                status_code=401,
                detail=(
                    "Google Drive credentials expired or revoked. "
                    f"Please reconnect. Error: {str(e)}"
                ),
            )

    return build("drive", "v3", credentials=creds)


@router.get("/status")
async def get_status(current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(GoogleCredentials).where(GoogleCredentials.user_id == current_user.id)
    )
    creds = result.scalar_one_or_none()
    return {
        "configured": settings.google_client_id is not None
        and settings.google_client_secret is not None,
        "connected": creds is not None,
        "email": current_user.email if creds else None,
    }


@router.get("/auth-url")
async def get_auth_url(current_user: CurrentUser):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=400,
            detail=(
                "Google Drive Client Credentials (ID & Secret) "
                "are not configured in your backend .env file."
            ),
        )

    client_config = {
        "web": {
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": [settings.google_redirect_uri],
        }
    }

    flow = Flow.from_client_config(
        client_config, scopes=["https://www.googleapis.com/auth/drive"]
    )
    flow.redirect_uri = settings.google_redirect_uri

    # Generate Google Consent screen URL
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )

    # Strip PKCE parameters to disable stateful code_verifier checks
    parsed_url = urlparse(authorization_url)
    query_params = dict(parse_qsl(parsed_url.query))
    query_params.pop("code_challenge", None)
    query_params.pop("code_challenge_method", None)

    new_query = urlencode(query_params)
    stripped_url = urlunparse(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment,
        )
    )

    return {"url": stripped_url}


@router.post("/callback")
async def oauth_callback(body: CallbackRequest, current_user: CurrentUser, db: DB):
    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=400, detail="Google client credentials not configured in backend .env."
        )

    import json
    import urllib.parse
    import urllib.request
    from datetime import UTC, datetime, timedelta

    # Exchange authorization code for token manually via urllib (completely robust & stateless)
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": body.code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    
    data_payload = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(token_url, data=data_payload, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            token_data = json.loads(res_body)
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode("utf-8")
        raise HTTPException(
            status_code=400, detail=f"Failed to retrieve access token from Google: {error_msg}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to connect to Google: {str(e)}"
        )

    expires_in = token_data.get("expires_in", 3600)
    expiry = datetime.now(UTC) + timedelta(seconds=expires_in)

    creds = Credentials(
        token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        scopes=token_data.get("scope", "https://www.googleapis.com/auth/drive").split(" "),
        expiry=expiry,
    )

    # Check if database record already exists
    result = await db.execute(
        select(GoogleCredentials).where(GoogleCredentials.user_id == current_user.id)
    )
    db_creds = result.scalar_one_or_none()

    if not db_creds:
        db_creds = GoogleCredentials(
            user_id=current_user.id,
            token=creds.token,
            refresh_token=creds.refresh_token,
            token_uri=creds.token_uri,
            client_id=creds.client_id,
            client_secret=creds.client_secret,
            scopes=",".join(creds.scopes),
            expiry=creds.expiry,
        )
        db.add(db_creds)
    else:
        db_creds.token = creds.token
        if creds.refresh_token:
            db_creds.refresh_token = creds.refresh_token
        db_creds.expiry = creds.expiry
        db_creds.scopes = ",".join(creds.scopes)

    await db.commit()
    return {"status": "success", "connected": True}


@router.post("/disconnect")
async def disconnect(current_user: CurrentUser, db: DB):
    result = await db.execute(
        select(GoogleCredentials).where(GoogleCredentials.user_id == current_user.id)
    )
    db_creds = result.scalar_one_or_none()
    if db_creds:
        await db.delete(db_creds)
        await db.commit()
    return {"status": "success", "connected": False}


@router.get("/files")
async def list_files(
    current_user: CurrentUser,
    db: DB,
    q: str | None = None,
    folder_id: str = "root",
    page_size: int = 50,
    page_token: str | None = None,
):
    service = await get_drive_service(current_user, db)

    query_parts = []
    if q:
        query_parts.append(f"name contains '{q}'")
    else:
        query_parts.append(f"'{folder_id}' in parents")

    query_parts.append("trashed = false")
    query_str = " and ".join(query_parts)

    try:
        results = (
            service.files()
            .list(
                q=query_str,
                pageSize=page_size,
                pageToken=page_token,
                fields=(
                    "nextPageToken, files(id, name, mimeType, size, "
                    "modifiedTime, thumbnailLink, iconLink)"
                ),
                orderBy="folder,name",
            )
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google Drive API error: {str(e)}")

    return {
        "files": results.get("files", []),
        "nextPageToken": results.get("nextPageToken"),
    }


@router.post("/upload")
async def upload_file(
    current_user: CurrentUser,
    db: DB,
    file: UploadFile = File(...),
    parent_id: str | None = None,
):
    service = await get_drive_service(current_user, db)

    file_metadata = {
        "name": file.filename,
    }
    if parent_id and parent_id != "root":
        file_metadata["parents"] = [parent_id]

    try:
        content = await file.read()
        media = MediaIoBaseUpload(
            BytesIO(content), mimetype=file.content_type, resumable=True
        )

        uploaded_file = (
            service.files()
            .create(
                body=file_metadata,
                media_body=media,
                fields="id, name, mimeType, size, modifiedTime",
            )
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")

    return uploaded_file


@router.post("/folders")
async def create_folder(
    body: CreateFolderRequest, current_user: CurrentUser, db: DB
):
    service = await get_drive_service(current_user, db)

    file_metadata = {
        "name": body.name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if body.parent_id and body.parent_id != "root":
        file_metadata["parents"] = [body.parent_id]

    try:
        folder = (
            service.files()
            .create(body=file_metadata, fields="id, name, mimeType")
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Folder creation failed: {str(e)}")

    return folder


@router.delete("/files/{file_id}")
async def delete_file(file_id: str, current_user: CurrentUser, db: DB):
    service = await get_drive_service(current_user, db)
    try:
        service.files().delete(fileId=file_id).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete file: {str(e)}")
    return {"status": "success"}


@router.get("/files/{file_id}/download")
async def download_file(file_id: str, current_user: CurrentUser, db: DB):
    service = await get_drive_service(current_user, db)
    try:
        file_meta = (
            service.files().get(fileId=file_id, fields="name, mimeType").execute()
        )
        file_name = file_meta.get("name", "download_file")
        mime_type = file_meta.get("mimeType", "application/octet-stream")

        is_google_doc = mime_type.startswith("application/vnd.google-apps.")
        if is_google_doc:
            export_mappings = {
                "application/vnd.google-apps.document": ("application/pdf", ".pdf"),
                "application/vnd.google-apps.spreadsheet": (
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    ".xlsx",
                ),
                "application/vnd.google-apps.presentation": (
                    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    ".pptx",
                ),
            }
            if mime_type in export_mappings:
                target_mime, ext = export_mappings[mime_type]
                request = (
                    service.files().export_media(fileId=file_id, mimeType=target_mime)
                )
                if not file_name.endswith(ext):
                    file_name += ext
                mime_type = target_mime
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Exporting this Google Apps file type is not supported.",
                )
        else:
            request = service.files().get_media(fileId=file_id)

        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        fh.seek(0)
        return StreamingResponse(
            fh,
            media_type=mime_type,
            headers={
                "Content-Disposition": f'attachment; filename="{file_name}"',
                "Access-Control-Expose-Headers": "Content-Disposition",
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to download file: {str(e)}"
        )


@router.post("/sync/{section}")
async def manual_sync(section: str, current_user: CurrentUser, db: DB):
    from app.gdrive_sync import sync_section_to_gdrive
    await sync_section_to_gdrive(current_user.id, section, db)
    return {"status": "success", "message": f"Successfully backed up {section} to Google Drive."}


@router.post("/restore/{section}")
async def manual_restore(section: str, current_user: CurrentUser, db: DB):
    from app.gdrive_sync import restore_section_from_gdrive
    success = await restore_section_from_gdrive(current_user.id, section, db)
    if not success:
        raise HTTPException(status_code=400, detail=f"Failed to restore {section}. Check if backup file exists.")
    return {"status": "success", "message": f"Successfully restored {section} from Google Drive."}
