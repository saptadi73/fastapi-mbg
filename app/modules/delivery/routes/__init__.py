from fastapi import APIRouter

from app.modules.delivery.routes.delivery_routes import router as delivery_router

router = APIRouter()
router.include_router(delivery_router)
