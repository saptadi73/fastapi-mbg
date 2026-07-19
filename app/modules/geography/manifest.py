from app.core.config.settings import get_settings
from app.modules.geography.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="geography",
    prefix=f"{get_settings().api_v1_prefix}/geography",
    tags=["Geography"],
    router=router,
)
