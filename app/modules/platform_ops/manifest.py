from app.modules.manifest import ModuleManifest
from app.modules.platform_ops.routes import router

manifest = ModuleManifest(
    name="platform_ops",
    prefix="/api/v1/platform",
    tags=["Platform"],
    router=router,
)
