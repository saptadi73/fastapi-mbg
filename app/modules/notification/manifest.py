from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.notification.routes import router

manifest = ModuleManifest(
    name="notification",
    prefix=f"{get_settings().api_v1_prefix}/notifications",
    tags=["Notification"],
    router=router,
)
