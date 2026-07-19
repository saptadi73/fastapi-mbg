from fastapi import APIRouter

from app.modules.production.routes.production_routes import router as production_router

router = APIRouter()
router.include_router(production_router)
