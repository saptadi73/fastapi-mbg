from app.core.config.settings import get_settings
from app.modules.asset.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="asset",
    prefix=f"{get_settings().api_v1_prefix}/assets",
    tags=["Asset"],
    router=router,
)
