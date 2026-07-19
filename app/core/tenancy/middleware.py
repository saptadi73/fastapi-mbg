from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.tenancy.context import set_current_sppg, set_current_tenant


class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        tenant_id = request.headers.get("X-Tenant-ID")
        sppg_id = request.headers.get("X-SPPG-ID")
        set_current_tenant(tenant_id)
        set_current_sppg(sppg_id)
        response = await call_next(request)
        if tenant_id:
            response.headers["X-Tenant-ID"] = tenant_id
        if sppg_id:
            response.headers["X-SPPG-ID"] = sppg_id
        return response
