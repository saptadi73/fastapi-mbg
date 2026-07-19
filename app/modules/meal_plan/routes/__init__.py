from fastapi import APIRouter

from app.modules.meal_plan.routes.meal_plan_routes import router as meal_plan_router

router = APIRouter()
router.include_router(meal_plan_router)
