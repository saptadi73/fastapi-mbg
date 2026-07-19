from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.sppg.routes import router

manifest = ModuleManifest(
    name="sppg",
    prefix=f"{get_settings().api_v1_prefix}/sppg",
    tags=["SPPG"],
    router=router,
)
