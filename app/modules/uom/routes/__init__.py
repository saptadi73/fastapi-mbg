from fastapi import APIRouter

from app.modules.uom.routes.uom_routes import router as uom_router

router = APIRouter()
router.include_router(uom_router)
