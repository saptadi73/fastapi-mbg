from fastapi import APIRouter

from app.modules.beneficiary.routes.beneficiary_routes import router as beneficiary_router

router = APIRouter()
router.include_router(beneficiary_router)
