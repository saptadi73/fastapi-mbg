from fastapi import APIRouter

from app.modules.reporting.routes.reporting_routes import router as reporting_router

router = APIRouter()
router.include_router(reporting_router, prefix="/reporting")
