from contextvars import ContextVar

tenant_id_context: ContextVar[str | None] = ContextVar("tenant_id", default=None)


def set_current_tenant(tenant_id: str | None) -> None:
    tenant_id_context.set(tenant_id)


def get_current_tenant() -> str | None:
    return tenant_id_context.get()
