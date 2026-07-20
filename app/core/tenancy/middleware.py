from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.tenancy.context import set_current_sppg, set_current_tenant


def _normalize_scope_header(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if normalized.lower() in {"undefined", "null", "none"}:
        return None
    return normalized


class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        tenant_id = _normalize_scope_header(request.headers.get("X-Tenant-ID"))
        sppg_id = _normalize_scope_header(request.headers.get("X-SPPG-ID"))
        set_current_tenant(tenant_id)
        set_current_sppg(sppg_id)
        response = await call_next(request)
        if tenant_id:
            response.headers["X-Tenant-ID"] = tenant_id
        if sppg_id:
            response.headers["X-SPPG-ID"] = sppg_id
        return response
