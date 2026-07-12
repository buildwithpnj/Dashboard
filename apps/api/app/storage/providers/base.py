from abc import ABC, abstractmethod
from typing import List, Dict


class BaseStorageProvider(ABC):
    """Abstract Base Class defining the interface for all Storage Providers in Warborn OS."""

    @abstractmethod
    async def upload(self, file_name: str, content_type: str, data: bytes) -> str:
        """Upload a file to the storage provider. Returns the remote file ID."""
        pass

    @abstractmethod
    async def download(self, file_id: str) -> bytes:
        """Download a file from the storage provider. Returns file content bytes."""
        pass

    @abstractmethod
    async def delete(self, file_id: str) -> None:
        """Delete a file from the storage provider."""
        pass

    @abstractmethod
    async def list(self, folder_id: str = "root") -> "List[dict]":
        """List files in the specified directory or folder."""
        pass

    @abstractmethod
    async def search(self, query: str) -> "List[dict]":
        """Search for files by matching criteria."""
        pass

    @abstractmethod
    async def move(self, file_id: str, dest_folder_id: str) -> None:
        """Move a file to another folder parent."""
        pass

    @abstractmethod
    async def copy(self, file_id: str, dest_folder_id: str) -> str:
        """Copy a file to another folder parent. Returns the copied file's new ID."""
        pass

    @abstractmethod
    async def rename(self, file_id: str, new_name: str) -> None:
        """Rename an existing file or directory."""
        pass

    @abstractmethod
    async def create_folder(self, name: str, parent_id: str | None = None) -> str:
        """Create a folder. Returns the created folder ID."""
        pass

    @abstractmethod
    async def get_metadata(self, file_id: str) -> dict:
        """Get raw metadata dictionary for a file."""
        pass

    @abstractmethod
    async def get_quota(self) -> tuple[int, int]:
        """Retrieve storage usage metrics. Returns a tuple of (used_bytes, total_bytes)."""
        pass
