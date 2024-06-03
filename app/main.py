from venv import logger

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.admin_panel.views import UserAdmin, BookingsAdmin, RoomsAdmin, HotelsAdmin
from app.bookings.router import router as router_bookings

from app.users.router import router as router_users
from app.hotels.router import router as router_hotels
from app.database import engine
from app.config import settings

from app.pages.router import router as router_pages
from app.images.router import router as router_images

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis

from sqladmin import Admin

from app.admin_panel.auth_admin import authentication_backend


app = FastAPI(
    title="Бронирование Отелей",
)

app.mount("/static", StaticFiles(directory="app/static"), "static")

app.include_router(router_hotels)
app.include_router(router_users)
app.include_router(router_bookings)

app.include_router(router_pages)
app.include_router(router_images)


@app.on_event("startup")    # <-- данный декоратор прогоняет код перед запуском FastAPI
def startup():
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                              encoding="utf8",
                              decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")


@app.on_event("shutdown")  # <-- данный декоратор прогоняет код после завершения программы
def shutdown_event():
    logger.info("Service exited")


admin = Admin(app, engine, authentication_backend=authentication_backend)
admin.add_view(UserAdmin)
admin.add_view(HotelsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(BookingsAdmin)
