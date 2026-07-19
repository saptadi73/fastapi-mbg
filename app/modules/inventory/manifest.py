from app.core.config.settings import get_settings
from app.modules.inventory.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="inventory",
    prefix=f"{get_settings().api_v1_prefix}/inventory",
    tags=["Inventory"],
    router=router,
)
