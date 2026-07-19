from app.core.config.settings import get_settings
from app.modules.delivery.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="delivery",
    prefix=f"{get_settings().api_v1_prefix}/delivery-orders",
    tags=["Delivery"],
    router=router,
)
