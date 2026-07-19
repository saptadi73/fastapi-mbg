from app.core.config.settings import get_settings
from app.modules.document.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="document",
    prefix=f"{get_settings().api_v1_prefix}",
    tags=["Document"],
    router=router,
)
