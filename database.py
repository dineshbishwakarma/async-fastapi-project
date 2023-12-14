from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import Base

DATABASE_URL = "sqlite+aiosqlite:////Users/dineshbishwakarma/Documents/pydantic-data-model-fastapi/social_media.db"

# Engine object will manage connection with our database
engine = create_async_engine(DATABASE_URL)

# async_sessionmaker generate sessions tied to our database engine
# it returns function
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Define dependency
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session # yield make session remains open until the end of the request


# Create table schema
async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)