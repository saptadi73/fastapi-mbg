from fastapi import APIRouter

from app.modules.document.routes.document_routes import router as document_router

router = APIRouter()
router.include_router(document_router, prefix="/documents")
