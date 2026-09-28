import uuid
from typing import Tuple, Union
from fastapi import UploadFile
from core.exceptions import BadRequestException, NotFoundException
from core.logging import get_logger
from core.storage.base import StorageProvider
from core.storage.validator import FileValidator, MAX_FILE_SIZE_BYTES
from models.resume import ResumeModel
from repositories.profile_repository import ProfileRepository
from repositories.resume_repository import ResumeRepository
from schemas.profile import ProfileUpdate
from schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate

logger = get_logger(__name__)


class ResumeService:
    """
    Candidate resume lifecycle service.
    Orchestrates file validation, secure storage abstraction, database persistence,
    and profile synchronisation.
    """

    def __init__(
        self,
        resume_repo: ResumeRepository,
        profile_repo: ProfileRepository,
        storage_provider: StorageProvider,
    ) -> None:
        self.resume_repo = resume_repo
        self.profile_repo = profile_repo
        self.storage_provider = storage_provider

    async def upload_resume(
        self,
        user_id: Union[uuid.UUID, str],
        file: UploadFile,
    ) -> ResumeResponse:
        """
        Validate, store, and record a new or replacement candidate resume.
        Automatically removes obsolete physical files on replacement.
        """
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        # 1. Read file stream with memory buffer limit
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise BadRequestException("File exceeds maximum allowed limit of 10 MB.")

        raw_filename = file.filename or "resume.pdf"
        content_type = file.content_type or "application/octet-stream"

        # 2. Strict Security Validation (Magic numbers, extension, anti-malware)
        ext, validated_mime = FileValidator.validate_resume_file(
            filename=raw_filename,
            content_type=content_type,
            content=content,
        )

        # 3. Generate secure UUID filename and isolated storage path:
        # uploads/resumes/{user_id}/{unique_uuid}.{ext}
        stored_filename = f"{uuid.uuid4()}{ext}"
        storage_relative_path = f"resumes/{user_id}/{stored_filename}"

        # 4. Check for existing resume (Replacement flow)
        existing_resume = await self.resume_repo.find_by_user(user_id)
        if existing_resume:
            logger.info(f"Replacing existing resume for user {user_id}. Cleaning up old file.")
            await self.storage_provider.delete_file(existing_resume.file_path)

        # 5. Persist to storage provider
        saved_path = await self.storage_provider.save_file(content, storage_relative_path)

        # 6. Database record upsert
        if existing_resume:
            updated = await self.resume_repo.update(
                existing_resume,
                ResumeUpdate(
                    original_filename=raw_filename,
                    stored_filename=stored_filename,
                    file_type=validated_mime,
                    file_size=len(content),
                    file_path=saved_path,
                ),
            )
            resume_record = updated
        else:
            created = await self.resume_repo.create(
                ResumeCreate(
                    user_id=user_id,
                    original_filename=raw_filename,
                    stored_filename=stored_filename,
                    file_type=validated_mime,
                    file_size=len(content),
                    file_path=saved_path,
                )
            )
            resume_record = created

        # 7. Synchronise Profile.resume_url
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile:
            await self.profile_repo.update(
                profile,
                ProfileUpdate(resume_url="/api/v1/resume/download"),
            )

        logger.info(f"Resume processed successfully for user {user_id}: {raw_filename}")
        return ResumeResponse.model_validate(resume_record)

    # CamelCase alias
    async def uploadResume(self, user_id: Union[uuid.UUID, str], file: UploadFile) -> ResumeResponse:
        return await self.upload_resume(user_id, file)

    async def get_resume(self, user_id: Union[uuid.UUID, str]) -> ResumeResponse:
        """
        Retrieve metadata of candidate resume without exposing internal filesystem paths.
        """
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        resume = await self.resume_repo.find_by_user(user_id)
        if not resume:
            raise NotFoundException(resource="Resume for user", identifier=str(user_id))

        return ResumeResponse.model_validate(resume)

    # CamelCase alias
    async def getResume(self, user_id: Union[uuid.UUID, str]) -> ResumeResponse:
        return await self.get_resume(user_id)

    async def delete_resume(self, user_id: Union[uuid.UUID, str]) -> bool:
        """
        Remove resume file from storage and purge database record.
        """
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        resume = await self.resume_repo.find_by_user(user_id)
        if not resume:
            raise NotFoundException(resource="Resume for user", identifier=str(user_id))

        # Delete physical file from storage provider
        await self.storage_provider.delete_file(resume.file_path)

        # Delete database record
        await self.resume_repo.delete(resume.id)

        # Clear Profile resume_url reference if present
        profile = await self.profile_repo.get_by_user_id(user_id)
        if profile and profile.resume_url:
            await self.profile_repo.update(profile, ProfileUpdate(resume_url=None))

        logger.info(f"Deleted resume for user {user_id}")
        return True

    # CamelCase alias
    async def deleteResume(self, user_id: Union[uuid.UUID, str]) -> bool:
        return await self.delete_resume(user_id)

    async def download_resume(
        self,
        user_id: Union[uuid.UUID, str],
    ) -> Tuple[bytes, str, str]:
        """
        Retrieve binary resume document along with original filename and MIME type.
        Returns: (file_bytes, original_filename, file_type)
        """
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)

        resume = await self.resume_repo.find_by_user(user_id)
        if not resume:
            raise NotFoundException(resource="Resume for user", identifier=str(user_id))

        content = await self.storage_provider.get_file(resume.file_path)
        return content, resume.original_filename, resume.file_type

    # CamelCase alias
    async def downloadResume(self, user_id: Union[uuid.UUID, str]) -> Tuple[bytes, str, str]:
        return await self.download_resume(user_id)
