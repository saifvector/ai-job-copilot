import urllib.parse
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, File, Response, UploadFile, status
from core.dependencies import get_current_user_id, get_resume_parser_service, get_resume_service
from schemas.common import ApiResponse
from schemas.resume import ResumeDeleteResponse, ResumeResponse
from schemas.resume_analysis import ResumeParseResponse
from services.resume_parser_service import ResumeParserService
from services.resume_service import ResumeService

router = APIRouter()


@router.post(
    "/upload",
    response_model=ApiResponse[ResumeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload or Replace Resume",
    description=(
        "Upload a candidate resume document (.pdf or .docx up to 10 MB). "
        "Performs magic bytes inspection and replaces any existing resume."
    ),
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume document file (.pdf or .docx)"),
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ApiResponse[ResumeResponse]:
    resume_data = await resume_service.upload_resume(user_id=user_id, file=file)
    return ApiResponse(
        data=resume_data,
        message="Resume uploaded and verified successfully.",
    )


@router.post(
    "/parse",
    response_model=ApiResponse[ResumeParseResponse],
    summary="Parse Active Resume with Gemini AI",
    description=(
        "Extracts text from the user's active resume, runs AI extraction via Gemini Pro/Flash fallback, "
        "validates structured schema, and persists skills, projects, education, experience, and certifications."
    ),
)
async def parse_resume(
    resume_id: Optional[uuid.UUID] = None,
    user_id: uuid.UUID = Depends(get_current_user_id),
    parser_service: ResumeParserService = Depends(get_resume_parser_service),
) -> ApiResponse[ResumeParseResponse]:
    parse_result = await parser_service.parse_resume(user_id=user_id, resume_id=resume_id)
    return ApiResponse(
        data=parse_result,
        message="Resume parsed and candidate intelligence extracted successfully.",
    )



@router.get(
    "",
    response_model=ApiResponse[ResumeResponse],
    summary="Get Resume Metadata",
    description="Retrieve metadata for the current user's active resume.",
)
async def get_resume(
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ApiResponse[ResumeResponse]:
    resume_data = await resume_service.get_resume(user_id=user_id)
    return ApiResponse(
        data=resume_data,
        message="Resume metadata retrieved successfully.",
    )


@router.delete(
    "",
    response_model=ApiResponse[ResumeDeleteResponse],
    summary="Delete Resume",
    description="Remove the active resume file from storage and delete the database record.",
)
async def delete_resume(
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ApiResponse[ResumeDeleteResponse]:
    await resume_service.delete_resume(user_id=user_id)
    return ApiResponse(
        data=ResumeDeleteResponse(success=True, message="Resume successfully deleted."),
        message="Resume deleted successfully.",
    )


@router.get(
    "/download",
    summary="Download Resume",
    description="Download the binary document with original filename Content-Disposition header.",
)
async def download_resume(
    user_id: uuid.UUID = Depends(get_current_user_id),
    resume_service: ResumeService = Depends(get_resume_service),
) -> Response:
    content, filename, mime_type = await resume_service.download_resume(user_id=user_id)

    # Encode filename for RFC 5987 compatibility in Content-Disposition
    encoded_filename = urllib.parse.quote(filename)
    disposition = f'attachment; filename="{filename}"; filename*=UTF-8\'\'{encoded_filename}'

    return Response(
        content=content,
        media_type=mime_type,
        headers={
            "Content-Disposition": disposition,
            "Content-Length": str(len(content)),
            "Cache-Control": "private, no-cache, no-store, must-revalidate",
        },
    )
