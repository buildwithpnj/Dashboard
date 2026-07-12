import io
import asyncio
import logging
from typing import Any, List, Dict
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

from app.storage.config import storage_settings
from app.storage.providers.base import BaseStorageProvider

logger = logging.getLogger("warborn_storage_google")


class GoogleDriveProvider(BaseStorageProvider):
    """Google Drive specific storage driver that runs blocking API commands in execution threads."""

    def __init__(
        self,
        refresh_token: str,
        folder_id: str | None = None,
        account_email: str = "",
        client_id: str | None = None,
        client_secret: str | None = None
    ):
        self.refresh_token = refresh_token
        self.folder_id = folder_id
        self.account_email = account_email
        self.client_id = client_id or storage_settings.google_client_id
        self.client_secret = client_secret or storage_settings.google_client_secret
        self.token_uri = "https://oauth2.googleapis.com/token"

    def _build_credentials(self) -> Credentials:
        """Create and validate Google OAuth credentials from the refresh token."""
        if not self.client_id or not self.client_secret:
            raise ValueError("Google client configuration missing (GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET).")
        
        creds = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri=self.token_uri,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=["https://www.googleapis.com/auth/drive"]
        )
        
        # Ensure credentials are valid and refresh access token if needed
        creds.refresh(Request())
        return creds

    async def _get_service(self) -> Any:
        """Build the discovery drive client service asynchronously."""
        creds = await asyncio.to_thread(self._build_credentials)
        return build("drive", "v3", credentials=creds)

    async def upload(self, file_name: str, content_type: str, data: bytes) -> str:
        """Upload a file to Google Drive under the designated root or folder parent."""
        service = await self._get_service()
        
        parent_id = self.folder_id or "root"
        file_metadata = {
            "name": file_name,
            "parents": [parent_id]
        }
        
        fh = io.BytesIO(data)
        media = MediaIoBaseUpload(fh, mimetype=content_type, resumable=True)
        
        def _execute_upload():
            return service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id"
            ).execute()

        result = await asyncio.to_thread(_execute_upload)
        file_id = result.get("id")
        logger.info(f"File '{file_name}' uploaded successfully. Remote ID: {file_id} (Provider: {self.account_email})")
        return file_id

    async def download(self, file_id: str) -> bytes:
        """Download file content bytes by streaming chunks from Google Drive."""
        service = await self._get_service()
        
        def _execute_download():
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            return fh.getvalue()

        data = await asyncio.to_thread(_execute_download)
        logger.info(f"File '{file_id}' downloaded successfully (Provider: {self.account_email})")
        return data

    async def delete(self, file_id: str) -> None:
        """Permanently delete a file from Google Drive."""
        service = await self._get_service()
        
        def _execute_delete():
            service.files().delete(fileId=file_id).execute()

        await asyncio.to_thread(_execute_delete)
        logger.info(f"File '{file_id}' deleted successfully (Provider: {self.account_email})")

    async def list(self, folder_id: str = "root") -> List[dict]:
        """List active files inside a parent folder directory."""
        service = await self._get_service()
        
        target_folder = folder_id if folder_id != "root" else (self.folder_id or "root")
        query = f"'{target_folder}' in parents and trashed = false"
        
        def _execute_list():
            results = service.files().list(
                q=query,
                fields="files(id, name, mimeType, size, modifiedTime)",
                pageSize=100
            ).execute()
            return results.get("files", [])

        files = await asyncio.to_thread(_execute_list)
        return files

    async def search(self, query: str) -> List[dict]:
        """Search active files matching name query."""
        service = await self._get_service()
        
        parent_folder = self.folder_id or "root"
        escaped_query = query.replace("'", "\\'")
        query_str = f"name contains '{escaped_query}' and '{parent_folder}' in parents and trashed = false"
        
        def _execute_search():
            results = service.files().list(
                q=query_str,
                fields="files(id, name, mimeType, size, modifiedTime)",
                pageSize=100
            ).execute()
            return results.get("files", [])

        files = await asyncio.to_thread(_execute_search)
        return files

    async def move(self, file_id: str, dest_folder_id: str) -> None:
        """Move a file by changing its parents."""
        service = await self._get_service()
        
        def _execute_move():
            # Retrieve existing parents to remove them
            file = service.files().get(fileId=file_id, fields="parents").execute()
            previous_parents = ",".join(file.get("parents", []))
            
            service.files().update(
                fileId=file_id,
                addParents=dest_folder_id,
                removeParents=previous_parents,
                fields="id, parents"
            ).execute()

        await asyncio.to_thread(_execute_move)
        logger.info(f"Moved file '{file_id}' to parent '{dest_folder_id}' (Provider: {self.account_email})")

    async def copy(self, file_id: str, dest_folder_id: str) -> str:
        """Copy a file to a destination folder."""
        service = await self._get_service()
        
        file_metadata = {
            "parents": [dest_folder_id]
        }
        
        def _execute_copy():
            result = service.files().copy(
                fileId=file_id,
                body=file_metadata,
                fields="id"
            ).execute()
            return result.get("id")

        new_id = await asyncio.to_thread(_execute_copy)
        logger.info(f"Copied file '{file_id}' to '{dest_folder_id}'. New ID: {new_id} (Provider: {self.account_email})")
        return new_id

    async def rename(self, file_id: str, new_name: str) -> None:
        """Rename an existing file or directory on Google Drive."""
        service = await self._get_service()
        
        file_metadata = {
            "name": new_name
        }
        
        def _execute_rename():
            service.files().update(
                fileId=file_id,
                body=file_metadata,
                fields="id, name"
            ).execute()

        await asyncio.to_thread(_execute_rename)
        logger.info(f"Renamed file '{file_id}' to '{new_name}' (Provider: {self.account_email})")

    async def create_folder(self, name: str, parent_id: str | None = None) -> str:
        """Create a new folder folder structure."""
        service = await self._get_service()
        
        target_parent = parent_id or self.folder_id or "root"
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [target_parent]
        }
        
        def _execute_create():
            result = service.files().create(
                body=file_metadata,
                fields="id"
            ).execute()
            return result.get("id")

        folder_id = await asyncio.to_thread(_execute_create)
        logger.info(f"Created folder '{name}'. ID: {folder_id} (Provider: {self.account_email})")
        return folder_id

    async def get_metadata(self, file_id: str) -> dict:
        """Get file metadata from Google Drive."""
        service = await self._get_service()
        
        def _execute_get_meta():
            return service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, modifiedTime, parents"
            ).execute()

        meta = await asyncio.to_thread(_execute_get_meta)
        return meta

    async def get_quota(self) -> tuple[int, int]:
        """Retrieve total storage quota metrics for the Google Drive account."""
        service = await self._get_service()
        
        def _execute_quota():
            about = service.about().get(fields="storageQuota").execute()
            quota = about.get("storageQuota", {})
            # usage and limit
            limit = int(quota.get("limit", 15 * 1024 * 1024 * 1024))  # default 15GB
            usage = int(quota.get("usage", 0))
            return usage, limit

        usage, limit = await asyncio.to_thread(_execute_quota)
        return usage, limit
