from fastapi import APIRouter

from app.modules.tenant.routes.tenant_routes import router as tenant_router

router = APIRouter()
router.include_router(tenant_router)
