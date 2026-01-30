# api/services/database_service.py
"""
Database connection and initialization service
Handles async Postgres connections using SQLAlchemy
"""
import os
from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from datetime import datetime, timedelta

from ..models.database import Base, MessageEvent
from ..config import settings


class DatabaseService:
    """
    Manages database connections and provides session handling.

    Usage:
        # Initialize on app startup
        await database_service.initialize()

        # Use in endpoints
        async with database_service.get_session() as session:
            # do database operations

        # Cleanup on shutdown
        await database_service.shutdown()
    """

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._initialized = False

    @property
    def database_url(self) -> Optional[str]:
        """
        Get the database URL from environment variables.
        Railway provides DATABASE_URL automatically when you add Postgres.
        """
        url = os.getenv("DATABASE_URL")
        if url:
            # Railway/Heroku use postgres:// but asyncpg needs postgresql+asyncpg://
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://") and "+asyncpg" not in url:
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url

    @property
    def is_configured(self) -> bool:
        """Check if database is configured"""
        return bool(self.database_url)

    @property
    def is_initialized(self) -> bool:
        """Check if database has been initialized"""
        return self._initialized

    async def initialize(self) -> bool:
        """
        Initialize the database connection and create tables.
        Call this on application startup.

        Returns:
            True if initialization successful, False otherwise
        """
        if not self.is_configured:
            print("⚠️ DATABASE_URL not configured - webhook storage disabled")
            return False

        try:
            print(f"🔌 Connecting to Postgres...")

            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                echo=settings.is_development,  # Log SQL in development
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True  # Verify connections before use
            )

            # Create session factory
            self.session_factory = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )

            # Create tables if they don't exist
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            self._initialized = True
            print("✅ Database initialized successfully")
            return True

        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            self._initialized = False
            return False

    async def shutdown(self):
        """
        Close database connections.
        Call this on application shutdown.
        """
        if self.engine:
            await self.engine.dispose()
            print("🔌 Database connections closed")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session for use in endpoints.

        Usage:
            async with database_service.get_session() as session:
                # do stuff
        """
        if not self._initialized or not self.session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def cleanup_old_events(self, retention_days: int = 90) -> int:
        """
        Delete events older than retention period.
        Run this periodically (e.g., daily via cron or scheduled task).

        Args:
            retention_days: Number of days to keep events (default 90)

        Returns:
            Number of deleted rows
        """
        if not self._initialized:
            return 0

        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)

        async with self.session_factory() as session:
            result = await session.execute(
                text("DELETE FROM message_events WHERE created_at < :cutoff"),
                {"cutoff": cutoff_date}
            )
            await session.commit()
            deleted_count = result.rowcount
            print(f"🧹 Cleaned up {deleted_count} events older than {retention_days} days")
            return deleted_count

    async def health_check(self) -> dict:
        """
        Check database connectivity.
        Useful for health check endpoints.
        """
        if not self._initialized:
            return {"status": "not_configured", "message": "DATABASE_URL not set"}

        try:
            async with self.session_factory() as session:
                await session.execute(text("SELECT 1"))
            return {"status": "healthy", "message": "Database connection OK"}
        except Exception as e:
            return {"status": "unhealthy", "message": str(e)}


# Singleton instance
database_service = DatabaseService()
