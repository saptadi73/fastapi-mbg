from app.core.config.settings import get_settings
from app.modules.ai.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="ai",
    prefix=f"{get_settings().api_v1_prefix}/ai",
    tags=["AI"],
    router=router,
)
