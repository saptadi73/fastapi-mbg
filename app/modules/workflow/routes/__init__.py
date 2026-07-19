from fastapi import APIRouter

from app.modules.workflow.routes.workflow_routes import router as workflow_router

router = APIRouter()
router.include_router(workflow_router, prefix="/workflows")
