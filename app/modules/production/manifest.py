from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.production.routes import router

manifest = ModuleManifest(
    name="production",
    prefix=f"{get_settings().api_v1_prefix}/production-orders",
    tags=["Production"],
    router=router,
)
