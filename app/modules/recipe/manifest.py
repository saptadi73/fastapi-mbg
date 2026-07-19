from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.recipe.routes import router

manifest = ModuleManifest(
    name="recipe",
    prefix=f"{get_settings().api_v1_prefix}/recipes",
    tags=["Recipe"],
    router=router,
)
