from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.workforce.routes import router

manifest = ModuleManifest(
    name="workforce",
    prefix=f"{get_settings().api_v1_prefix}/workforce",
    tags=["Workforce"],
    router=router,
)
