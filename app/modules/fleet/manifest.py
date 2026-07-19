from app.core.config.settings import get_settings
from app.modules.fleet.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="fleet",
    prefix=f"{get_settings().api_v1_prefix}/fleet",
    tags=["Fleet"],
    router=router,
)
