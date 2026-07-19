from app.core.config.settings import get_settings
from app.modules.accounting.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="accounting",
    prefix=f"{get_settings().api_v1_prefix}",
    tags=["Accounting"],
    router=router,
)
