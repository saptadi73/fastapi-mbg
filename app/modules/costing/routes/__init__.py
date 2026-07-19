from fastapi import APIRouter

from app.modules.costing.routes.costing_routes import router as costing_router

router = APIRouter()
router.include_router(costing_router, prefix="/costing")
