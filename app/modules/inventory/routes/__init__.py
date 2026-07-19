from fastapi import APIRouter

from app.modules.inventory.routes.stock_routes import router as stock_router
from app.modules.inventory.routes.warehouse_routes import router as warehouse_router

router = APIRouter()
router.include_router(warehouse_router)
router.include_router(stock_router)
