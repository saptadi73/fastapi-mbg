from app.core.config.settings import get_settings
from app.modules.feedback.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="feedback",
    prefix=f"{get_settings().api_v1_prefix}/feedback",
    tags=["Feedback"],
    router=router,
)
