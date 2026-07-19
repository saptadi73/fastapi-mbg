from app.core.config.settings import get_settings
from app.modules.costing.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="costing",
    prefix=f"{get_settings().api_v1_prefix}",
    tags=["Costing"],
    router=router,
)
