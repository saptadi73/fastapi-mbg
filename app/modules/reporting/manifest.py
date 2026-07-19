from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.reporting.routes import router

manifest = ModuleManifest(
    name="reporting",
    prefix=f"{get_settings().api_v1_prefix}",
    tags=["Reporting"],
    router=router,
)
