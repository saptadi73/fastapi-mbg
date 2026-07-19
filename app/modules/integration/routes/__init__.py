from fastapi import APIRouter

from app.modules.integration.routes.integration_routes import router as integration_router

router = APIRouter()
router.include_router(integration_router, prefix="/integration")
