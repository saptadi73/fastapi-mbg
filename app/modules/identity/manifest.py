from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.identity.routes import router

manifest = ModuleManifest(
    name="identity",
    prefix=f"{get_settings().api_v1_prefix}/identity",
    tags=["Identity"],
    router=router,
)
