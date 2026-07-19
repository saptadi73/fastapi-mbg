from fastapi import APIRouter

from app.modules.audit.routes.audit_routes import router as audit_router

router = APIRouter()
router.include_router(audit_router, prefix="/audit")
