from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.uom.routes import router

manifest = ModuleManifest(
    name="uom",
    prefix=f"{get_settings().api_v1_prefix}/uoms",
    tags=["UoM"],
    router=router,
)
