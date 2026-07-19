from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.program.routes import router

manifest = ModuleManifest(
    name="program",
    prefix=f"{get_settings().api_v1_prefix}",
    tags=["Program"],
    router=router,
)
