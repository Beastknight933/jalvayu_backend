from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings


# Create the SQLAlchemy AsyncEngine
engine: AsyncEngine = create_async_engine(
    str(settings.SQLALCHEMY_DATABASE_URI) if settings.SQLALCHEMY_DATABASE_URI else "",
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True, # Proactively check if connection is alive
    pool_size=20,
    max_overflow=10
)

# AsyncSession factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

async def get_db_session():
    """
    Dependency function that yields a database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
