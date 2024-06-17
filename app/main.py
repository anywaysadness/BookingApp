import time
from urllib.request import Request
from venv import logger

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_versioning import VersionedFastAPI
from redis import asyncio as aioredis
from sqladmin import Admin
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from app.admin_panel.auth_admin import authentication_backend
from app.admin_panel.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UserAdmin
from app.bookings.router import router as router_bookings
from app.config import settings
from app.database import engine
from app.hotels.router import router as router_hotels
from app.images.router import router as router_images
from app.logger import logger
from app.pages.router import router as router_pages
from app.users.router import router as router_users
from app.importer.router import router as router_import
app = FastAPI(
    title="Бронирование Отелей",
)


app.include_router(router_hotels)
app.include_router(router_users)
app.include_router(router_bookings)

app.include_router(router_import)

app.include_router(router_pages)
app.include_router(router_images)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        "Request execution time", extra={"process_time": round(process_time, 4)}
    )
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.on_event("startup")  # <-- данный декоратор прогоняет код перед запуском FastAPI
def startup():
    redis = aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis), prefix="cache")


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"]
)
instrumentator.instrument(app).expose(app)


@app.on_event(
    "shutdown"
)  # <-- данный декоратор прогоняет код после завершения программы
def shutdown_event():
    logger.info("Service exited")


admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)

app.mount("/static", StaticFiles(directory="app/static"), "static")
