from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.procurement.routes import router

manifest = ModuleManifest(
    name="procurement",
    prefix=f"{get_settings().api_v1_prefix}/procurement",
    tags=["Procurement"],
    router=router,
)
