from fastapi import APIRouter

from app.modules.geography.routes.school_routes import router as school_router

router = APIRouter()
router.include_router(school_router, prefix="/schools")
