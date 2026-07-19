from fastapi import APIRouter

from app.modules.product.routes.product_routes import router as product_router

router = APIRouter()
router.include_router(product_router)
