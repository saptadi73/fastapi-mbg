from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.workflow.routes import router

manifest = ModuleManifest(
    name="workflow",
    prefix=f"{get_settings().api_v1_prefix}",
    tags=["Workflow"],
    router=router,
)
