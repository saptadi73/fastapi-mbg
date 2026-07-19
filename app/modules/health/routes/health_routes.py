from fastapi import APIRouter, Request

from app.core.database.session import database_is_ready
from app.support.responses.envelope import success_response

router = APIRouter()


@router.get("/health/live")
async def live(request: Request) -> dict:
    return success_response(
        code="HEALTH_LIVE",
        message="Service hidup.",
        data={"status": "alive"},
        meta={"request_id": request.state.request_id},
    )


@router.get("/health/ready")
async def ready(request: Request) -> dict:
    db_ready = await database_is_ready()
    return success_response(
        code="HEALTH_READY",
        message="Service siap menerima request." if db_ready else "Service bootstrap tanpa database.",
        data={"status": "ready", "database_ready": db_ready},
        meta={"request_id": request.state.request_id},
    )


@router.get("/health/database")
async def database(request: Request) -> dict:
    db_ready = await database_is_ready()
    return success_response(
        code="HEALTH_DATABASE",
        message="Database siap." if db_ready else "Database belum dikonfigurasi atau belum siap.",
        data={"ready": db_ready},
        meta={"request_id": request.state.request_id},
    )
