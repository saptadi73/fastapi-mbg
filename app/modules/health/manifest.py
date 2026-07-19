from app.modules.manifest import ModuleManifest
from app.modules.health.routes import router

manifest = ModuleManifest(
    name="health",
    prefix="",
    tags=["Health"],
    router=router,
)
