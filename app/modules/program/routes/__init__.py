from fastapi import APIRouter

from app.modules.program.routes.program_routes import router as program_router

router = APIRouter()
router.include_router(program_router)
