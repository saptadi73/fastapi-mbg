from fastapi import APIRouter

from app.modules.platform_ops.routes.platform_ops_routes import router as platform_ops_router

router = APIRouter()
router.include_router(platform_ops_router)
