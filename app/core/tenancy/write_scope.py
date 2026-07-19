from uuid import UUID

from app.core.tenancy.context import get_current_sppg, get_current_tenant
from app.support.exceptions.base import BadRequestException, ForbiddenException


def enforce_tenant_write_scope(tenant_id: UUID) -> None:
    current_tenant = get_current_tenant()
    if current_tenant is None:
        return
    try:
        scoped_tenant_id = UUID(current_tenant)
    except ValueError as exc:
        raise BadRequestException(
            code="INVALID_TENANT_CONTEXT",
            message="Header X-Tenant-ID tidak valid.",
        ) from exc
    if scoped_tenant_id != tenant_id:
        raise ForbiddenException(
            code="TENANT_WRITE_SCOPE_VIOLATION",
            message="Tenant pada payload tidak sesuai dengan scope request.",
        )


def enforce_sppg_write_scope(sppg_id: UUID) -> None:
    current_sppg = get_current_sppg()
    if current_sppg is None:
        return
    try:
        scoped_sppg_id = UUID(current_sppg)
    except ValueError as exc:
        raise BadRequestException(
            code="INVALID_SPPG_CONTEXT",
            message="Header X-SPPG-ID tidak valid.",
        ) from exc
    if scoped_sppg_id != sppg_id:
        raise ForbiddenException(
            code="SPPG_WRITE_SCOPE_VIOLATION",
            message="SPPG pada payload tidak sesuai dengan scope request.",
        )
