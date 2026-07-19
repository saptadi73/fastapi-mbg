from app.core.config.settings import get_settings
from app.modules.government_claim.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="government_claim",
    prefix=f"{get_settings().api_v1_prefix}/government-claims",
    tags=["Government Claim"],
    router=router,
)
