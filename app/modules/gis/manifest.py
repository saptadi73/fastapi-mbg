from app.core.config.settings import get_settings
from app.modules.gis.routes import router
from app.modules.manifest import ModuleManifest

manifest = ModuleManifest(
    name="gis",
    prefix=f"{get_settings().api_v1_prefix}/gis",
    tags=["GIS"],
    router=router,
)
