"""
Axorks OS — User Service

Profile retrieval and updates.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import NotFoundError
from src.modules.users.models import User
from src.modules.users.schemas import UserUpdate


class UserService:
    """Service for user profile operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: UUID) -> User:
        """Get user by ID or raise NotFoundError."""
        query = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User", str(user_id))
        return user

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address."""
        query = select(User).where(User.email == email, User.deleted_at.is_(None))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_profile(self, user_id: UUID, data: UserUpdate) -> User:
        """Update user profile fields."""
        user = await self.get_by_id(user_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update_preferences(self, user_id: UUID, preferences: dict) -> User:
        """Merge new preferences into existing user preferences."""
        user = await self.get_by_id(user_id)
        current = user.preferences or {}
        current.update({k: v for k, v in preferences.items() if v is not None})
        user.preferences = current
        await self.db.flush()
        await self.db.refresh(user)
        return user
