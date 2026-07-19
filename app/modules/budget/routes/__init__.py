from fastapi import APIRouter

from app.modules.budget.routes.budget_routes import router as budget_router

router = APIRouter()
router.include_router(budget_router)
