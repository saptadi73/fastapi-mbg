from fastapi import APIRouter

from app.modules.procurement.routes.purchase_request_routes import router as purchase_request_router

router = APIRouter()
router.include_router(purchase_request_router)
