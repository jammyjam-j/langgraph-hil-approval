from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from .router import api_router
from .dependencies import get_db_session
from .middleware import exception_handler_middleware
from .config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Human‑in‑the‑loop approval workflow powered by LangGraph and FastAPI",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.middleware("http")
async def db_session_middleware(request, call_next):
    async with get_db_session() as session:
        request.state.db = session
        response = await call_next(request)
    return response

app.add_exception_handler(Exception, exception_handler_middleware)

app.include_router(api_router, prefix="/api")