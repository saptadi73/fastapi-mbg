from contextvars import ContextVar

tenant_id_context: ContextVar[str | None] = ContextVar("tenant_id", default=None)
sppg_id_context: ContextVar[str | None] = ContextVar("sppg_id", default=None)


def set_current_tenant(tenant_id: str | None) -> None:
    tenant_id_context.set(tenant_id)


def get_current_tenant() -> str | None:
    return tenant_id_context.get()


def set_current_sppg(sppg_id: str | None) -> None:
    sppg_id_context.set(sppg_id)


def get_current_sppg() -> str | None:
    return sppg_id_context.get()
