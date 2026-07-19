from app.core.config.settings import get_settings
from app.modules.integration.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="integration",
    prefix=f"{get_settings().api_v1_prefix}",
    tags=["Integration"],
    router=router,
)
