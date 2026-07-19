from app.core.config.settings import get_settings
from app.modules.budget.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="budget",
    prefix=f"{get_settings().api_v1_prefix}",
    tags=["Budget"],
    router=router,
)
