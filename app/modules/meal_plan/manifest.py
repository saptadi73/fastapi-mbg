from app.core.config.settings import get_settings
from app.modules.manifest import ModuleManifest
from app.modules.meal_plan.routes import router

manifest = ModuleManifest(
    name="meal_plan",
    prefix=f"{get_settings().api_v1_prefix}/meal-plans",
    tags=["MealPlan"],
    router=router,
)
