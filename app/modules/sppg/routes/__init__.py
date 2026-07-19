from fastapi import APIRouter

from app.modules.sppg.routes.sppg_routes import router as sppg_router

router = APIRouter()
router.include_router(sppg_router)
