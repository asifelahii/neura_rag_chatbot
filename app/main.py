import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.conversations.store import conversation_store
from app.core.config import settings
from app.middleware.request_context import RequestContextMiddleware
from app.security.rate_limiter import rate_limiter


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(name)s "
        "%(message)s"
    ),
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "Starting %s",
        settings.app_name,
    )

    yield

    await conversation_store.close()
    await rate_limiter.close()

    logger.info(
        "Neura application resources closed successfully"
    )


app = FastAPI(
    title=settings.app_name,
    description="AI chatbot microservice for Neura Solutions Limited",
    version=settings.app_version,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=[
        "Content-Type",
        "X-Request-ID",
    ],
)

app.add_middleware(RequestContextMiddleware)

app.include_router(chat_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Neura RAG Chatbot",
    }

@app.get("/ready", tags=["Health"])
async def readiness_check():
    try:
        store_ready = (
            await conversation_store.ping()
        )

        rate_limiter_ready = (
            await rate_limiter.ping()
        )

    except Exception:
        logger.exception(
            "Application readiness check failed"
        )

        raise HTTPException(
            status_code=503,
            detail="Service is not ready.",
        )

    if not (
        store_ready
        and rate_limiter_ready
    ):
        raise HTTPException(
            status_code=503,
            detail="Service is not ready.",
        )

    return {
        "status": "ready",
        "dependencies": {
            "conversation_store": "healthy",
            "rate_limiter": "healthy",
        },
    }