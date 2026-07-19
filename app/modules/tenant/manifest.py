from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.tenant.routes import router

manifest = ModuleManifest(
    name="tenant",
    prefix=f"{get_settings().api_v1_prefix}/tenants",
    tags=["Tenant"],
    router=router,
)
