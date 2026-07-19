import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.support.exceptions.base import AppException
from app.support.responses.envelope import error_response

logger = logging.getLogger(__name__)


def _request_meta(request: Request) -> dict[str, str]:
    request_id = getattr(request.state, "request_id", None)
    return {"request_id": request_id} if request_id else {}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                code=exc.code,
                message=exc.message,
                errors=exc.errors,
                meta=_request_meta(request),
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        errors = [
            {
                "field": ".".join(str(part) for part in error["loc"]),
                "detail": error["msg"],
            }
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=error_response(
                code="REQUEST_VALIDATION_ERROR",
                message="Validasi request gagal.",
                errors=errors,
                meta=_request_meta(request),
            ),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Permintaan tidak dapat diproses."
        code = f"HTTP_{exc.status_code}"
        errors = [] if isinstance(exc.detail, str) else [{"detail": str(exc.detail)}]
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(
                code=code,
                message=detail,
                errors=errors,
                meta=_request_meta(request),
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content=error_response(
                code="INTERNAL_SERVER_ERROR",
                message="Terjadi kesalahan internal pada server.",
                meta=_request_meta(request),
            ),
        )
