from datetime import datetime, timezone
from typing import Any

from fastapi.encoders import jsonable_encoder


def success_response(
    *,
    code: str,
    message: str,
    data: Any = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload_meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **(meta or {}),
    }
    return {
        "success": True,
        "code": code,
        "message": message,
        "data": jsonable_encoder(data),
        "meta": payload_meta,
    }


def error_response(
    *,
    code: str,
    message: str,
    errors: list[dict[str, Any]] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload_meta = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **(meta or {}),
    }
    return {
        "success": False,
        "code": code,
        "message": message,
        "errors": errors or [],
        "meta": payload_meta,
    }
