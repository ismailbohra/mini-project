from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.comments.router import router as comments_router
from app.config.settings import settings
from app.moderator.router import router as moderator_router
from app.notifications.router import router as notifications_router
from app.posts.router import router as posts_router
from app.users.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    import app.core.event_bus as event_bus_module
    from app.core.event_bus import RedisEventBus

    event_bus_module.event_bus = RedisEventBus(settings.REDIS_URL)
    await event_bus_module.event_bus.connect()

    from app.notifications.subscribers import register_subscribers

    await register_subscribers()
    await event_bus_module.event_bus.start_listener()

    yield

    await event_bus_module.event_bus.disconnect()


app = FastAPI(
    title="Mini Project API",
    description="Backend API for Mini Project",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(posts_router)
app.include_router(comments_router)
app.include_router(moderator_router)
app.include_router(notifications_router)

# Mount assets directory to serve static files (uploaded images)
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
