from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.product.routes import router

manifest = ModuleManifest(
    name="product",
    prefix=f"{get_settings().api_v1_prefix}/products",
    tags=["Product"],
    router=router,
)
