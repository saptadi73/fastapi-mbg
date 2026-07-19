from fastapi import APIRouter

from app.modules.quality.routes.quality_routes import router as quality_router

router = APIRouter()
router.include_router(quality_router, prefix="/quality")
