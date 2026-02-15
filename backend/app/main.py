from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.comments.router import router as comments_router
from app.middleware import RoleVerificationMiddleware
from app.moderator.router import router as moderator_router
from app.notifications.router import router as notifications_router
from app.posts.router import router as posts_router
from app.users.router import router as users_router
from app.utils.exceptions import (
    AppException,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.utils.logging import get_logger, init_logging

init_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.utils.event_bus as event_bus_module
    import app.utils.redis_cache as redis_cache_module
    from app.config.redis import redis_client
    from app.utils.event_bus import RedisEventBus
    from app.utils.redis_cache import RedisCache

    logger.info("Starting application...")

    # Connect centralized Redis client
    client = await redis_client.connect()
    logger.info("Redis client connected")

    # Initialize event bus and cache with shared client
    event_bus_module.event_bus = RedisEventBus(client)
    await event_bus_module.event_bus.connect()
    logger.info("Redis event bus initialized")

    redis_cache_module.redis_cache = RedisCache(client)
    logger.info("Redis cache initialized")

    from app.notifications.subscribers import register_subscribers

    await register_subscribers()
    await event_bus_module.event_bus.start_listener()
    logger.info("Event listeners started")

    yield

    logger.info("Shutting down application...")
    await event_bus_module.event_bus.disconnect()
    logger.info("Redis event bus disconnected")

    # Disconnect centralized Redis client
    await redis_client.disconnect()
    logger.info("Redis client disconnected")


app = FastAPI(
    title="Mini Project API",
    description="Backend API for Mini Project",
    version="1.0.0",
    lifespan=lifespan,
    root_path="/api",
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add role verification middleware to check if user's role has been modified
app.add_middleware(RoleVerificationMiddleware)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(moderator_router)
app.include_router(notifications_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}


ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
