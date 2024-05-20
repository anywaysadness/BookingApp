from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import DATABASE_URL
# DB_HOST = "192.168.143.15"
# DB_PORT = 5432
# DB_USER = "postgres"
# DB_PASS = "postgres"
# DB_NAME = "PGAnywayFastAPI"


engine = create_async_engine(DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
