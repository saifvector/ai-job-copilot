from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.exceptions import AppException
from core.logging import correlation_id_ctx, get_logger

logger = get_logger("error_handler")


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register global exception handlers for standardized, structured error responses.
    Guarantees categorized responses: Validation, Authentication, Database, AI Provider, External Provider.
    """

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        cid = correlation_id_ctx.get() or request.headers.get("X-Correlation-ID", "")
        logger.warning(
            f"Domain exception on {request.url.path}: {exc.message} "
            f"(code: {exc.code}, category: {exc.category})"
        )
        try:
            from services.monitoring_service import metrics_collector
            metrics_collector.record_error(exc.category)
        except Exception:
            pass
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "category": exc.category,
                    "details": exc.details,
                    "request_id": cid,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": cid,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        cid = correlation_id_ctx.get() or request.headers.get("X-Correlation-ID", "")
        errors = []
        for err in exc.errors():
            errors.append({
                "loc": [str(loc_item) for loc_item in err.get("loc", [])],
                "msg": err.get("msg", "Invalid value"),
                "type": err.get("type", "value_error"),
            })
        logger.info(f"Validation error on {request.url.path}: {errors}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed. Please check the provided fields.",
                    "category": "Validation",
                    "details": errors,
                    "request_id": cid,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": cid,
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        cid = correlation_id_ctx.get() or request.headers.get("X-Correlation-ID", "")
        category = "Authentication" if exc.status_code in (401, 403) else "Validation"
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "category": category,
                    "details": {},
                    "request_id": cid,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": cid,
            },
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        cid = correlation_id_ctx.get() or request.headers.get("X-Correlation-ID", "")
        logger.error(f"Database error on {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "A database operation failed or connection pool timed out.",
                    "category": "Database",
                    "details": {},
                    "request_id": cid,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": cid,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        cid = correlation_id_ctx.get() or request.headers.get("X-Correlation-ID", "")
        logger.error(f"Unhandled system exception on {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected internal server error occurred.",
                    "category": "General",
                    "details": {},
                    "request_id": cid,
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "correlation_id": cid,
            },
        )
