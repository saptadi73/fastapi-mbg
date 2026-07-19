from fastapi import APIRouter

from app.modules.recipe.routes.recipe_routes import router as recipe_router

router = APIRouter()
router.include_router(recipe_router)
