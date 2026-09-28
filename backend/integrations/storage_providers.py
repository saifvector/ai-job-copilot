from abc import abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from integrations.base import IntegrationProvider


class StorageIntegrationProvider(IntegrationProvider):
    """
    Base cloud storage integration providing automated resume backups, report exports, and versioning.
    """
    @property
    def category(self) -> str:
        return "storage"

    @property
    def capabilities(self) -> List[str]:
        return ["resume_backup", "report_export", "resume_version_storage"]

    @abstractmethod
    async def backup_resume(
        self,
        connection_metadata: Dict[str, Any],
        filename: str,
        content: bytes,
        target_folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Saves a candidate resume document into cloud drive storage."""
        pass

    @abstractmethod
    async def export_report(
        self,
        connection_metadata: Dict[str, Any],
        filename: str,
        content: bytes,
        target_folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Uploads an exported PDF/CSV report to user's cloud storage."""
        pass

    @abstractmethod
    async def store_resume_version(
        self,
        connection_metadata: Dict[str, Any],
        version_label: str,
        filename: str,
        content: bytes,
    ) -> Dict[str, Any]:
        """Stores a tailored resume snapshot under an organized folder structure."""
        pass


class GoogleDriveProvider(StorageIntegrationProvider):
    @property
    def provider_id(self) -> str:
        return "google_drive"

    @property
    def display_name(self) -> str:
        return "Google Drive"

    @property
    def description(self) -> str:
        return "Back up resumes, archive tailored versions, and store analytics exports in Google Drive folders."

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "root_folder": auth_payload.get("root_folder", "AI Job Copilot"),
            "access_token": auth_payload.get("access_token", "ya29.mock_gdrive_token"),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }

    async def disconnect(self, connection_metadata: Dict[str, Any]) -> bool:
        return True

    async def health_check(self, connection_metadata: Dict[str, Any]) -> bool:
        return bool(connection_metadata.get("access_token"))

    async def backup_resume(
        self,
        connection_metadata: Dict[str, Any],
        filename: str,
        content: bytes,
        target_folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        file_id = f"gdrive_file_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "provider": self.provider_id,
            "file_id": file_id,
            "filename": filename,
            "size_bytes": len(content),
            "folder": target_folder or connection_metadata.get("root_folder", "AI Job Copilot/Resumes"),
            "web_view_link": f"https://drive.google.com/file/d/{file_id}/view",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

    async def export_report(
        self,
        connection_metadata: Dict[str, Any],
        filename: str,
        content: bytes,
        target_folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        file_id = f"gdrive_rep_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "provider": self.provider_id,
            "file_id": file_id,
            "filename": filename,
            "size_bytes": len(content),
            "folder": target_folder or "AI Job Copilot/Reports",
            "web_view_link": f"https://drive.google.com/file/d/{file_id}/view",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

    async def store_resume_version(
        self,
        connection_metadata: Dict[str, Any],
        version_label: str,
        filename: str,
        content: bytes,
    ) -> Dict[str, Any]:
        return await self.backup_resume(
            connection_metadata=connection_metadata,
            filename=f"{version_label}_{filename}",
            content=content,
            target_folder=f"AI Job Copilot/Versions/{version_label}",
        )


class DropboxProvider(StorageIntegrationProvider):
    @property
    def provider_id(self) -> str:
        return "dropbox"

    @property
    def display_name(self) -> str:
        return "Dropbox"

    @property
    def description(self) -> str:
        return "Sync resume versions and application documents automatically to your personal or team Dropbox."

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "access_token": auth_payload.get("access_token", "sl.mock_dropbox_token"),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }

    async def disconnect(self, connection_metadata: Dict[str, Any]) -> bool:
        return True

    async def health_check(self, connection_metadata: Dict[str, Any]) -> bool:
        return bool(connection_metadata.get("access_token"))

    async def backup_resume(
        self,
        connection_metadata: Dict[str, Any],
        filename: str,
        content: bytes,
        target_folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        path = f"/{target_folder or 'AI_Job_Copilot'}/{filename}"
        return {
            "provider": self.provider_id,
            "path": path,
            "size_bytes": len(content),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

    async def export_report(
        self,
        connection_metadata: Dict[str, Any],
        filename: str,
        content: bytes,
        target_folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        path = f"/{target_folder or 'AI_Job_Copilot/Reports'}/{filename}"
        return {
            "provider": self.provider_id,
            "path": path,
            "size_bytes": len(content),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

    async def store_resume_version(
        self,
        connection_metadata: Dict[str, Any],
        version_label: str,
        filename: str,
        content: bytes,
    ) -> Dict[str, Any]:
        return await self.backup_resume(
            connection_metadata=connection_metadata,
            filename=f"{version_label}_{filename}",
            content=content,
            target_folder=f"AI_Job_Copilot/Versions/{version_label}",
        )


class OneDriveProvider(StorageIntegrationProvider):
    @property
    def provider_id(self) -> str:
        return "onedrive"

    @property
    def display_name(self) -> str:
        return "Microsoft OneDrive"

    @property
    def description(self) -> str:
        return "Archive candidate assets and career reports to OneDrive personal or corporate SharePoint libraries."

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "access_token": auth_payload.get("access_token", "mock_onedrive_token"),
            "connected_at": datetime.now(timezone.utc).isoformat(),
        }

    async def disconnect(self, connection_metadata: Dict[str, Any]) -> bool:
        return True

    async def health_check(self, connection_metadata: Dict[str, Any]) -> bool:
        return bool(connection_metadata.get("access_token"))

    async def backup_resume(
        self,
        connection_metadata: Dict[str, Any],
        filename: str,
        content: bytes,
        target_folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "provider": self.provider_id,
            "file_id": f"onedrive_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "filename": filename,
            "size_bytes": len(content),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

    async def export_report(
        self,
        connection_metadata: Dict[str, Any],
        filename: str,
        content: bytes,
        target_folder: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "provider": self.provider_id,
            "file_id": f"onedrive_rep_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "filename": filename,
            "size_bytes": len(content),
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }

    async def store_resume_version(
        self,
        connection_metadata: Dict[str, Any],
        version_label: str,
        filename: str,
        content: bytes,
    ) -> Dict[str, Any]:
        return await self.backup_resume(
            connection_metadata=connection_metadata,
            filename=f"{version_label}_{filename}",
            content=content,
            target_folder=f"AI_Job_Copilot/Versions/{version_label}",
        )
