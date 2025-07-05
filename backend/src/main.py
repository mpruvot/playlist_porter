"""Main application for Playlist Porter."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import health
from src.api.router import router as providers_router
from src.core.config import app_config
from src.infrastructure.logging import get_logger, setup_logging

setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    # Startup
    logger.info(f"Starting Playlist Porter ({app_config.environment})")

    yield

    # Shutdown
    logger.info("Shutting down...")


app = FastAPI(
    title=app_config.title,
    description=app_config.description,
    version=app_config.version,
    debug=app_config.debug,
    lifespan=lifespan,
)

# CORS configuration - Fixed for credentials support
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "https://localhost:3000",
    "https://localhost:3001",
]

# Add production domains if not in development
if app_config.environment == "production":
    allowed_origins.extend(
        [
            "https://your-domain.com",
            "https://www.your-domain.com",
        ]
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(providers_router, prefix="/playlists", tags=["Music Providers"])
