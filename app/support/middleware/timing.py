from time import perf_counter

from fastapi import FastAPI, Request


def register_timing_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_process_time(request: Request, call_next):
        started_at = perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time"] = f"{perf_counter() - started_at:.6f}"
        return response
