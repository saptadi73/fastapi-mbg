from app.core.config.settings import get_settings
from app.modules.funding.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="funding",
    prefix=f"{get_settings().api_v1_prefix}/funding",
    tags=["Funding"],
    router=router,
)
