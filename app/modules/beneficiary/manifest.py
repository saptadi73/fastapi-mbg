from app.core.config.settings import get_settings
from app.modules.beneficiary.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="beneficiary",
    prefix=f"{get_settings().api_v1_prefix}/beneficiaries",
    tags=["Beneficiary"],
    router=router,
)
