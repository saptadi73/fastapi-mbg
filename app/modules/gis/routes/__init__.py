from fastapi import APIRouter

from app.modules.gis.routes.gis_routes import router as gis_router

router = APIRouter()
router.include_router(gis_router)
