from fastapi import APIRouter

from app.modules.accounting.routes.accounting_routes import router as accounting_router

router = APIRouter()
router.include_router(accounting_router)
