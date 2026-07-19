from app.core.config.settings import get_settings
from app.modules.audit.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="audit",
    prefix=f"{get_settings().api_v1_prefix}",
    tags=["Audit"],
    router=router,
)
