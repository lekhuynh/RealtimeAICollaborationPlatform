from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreateByAdmin, UserUpdateByAdmin
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User, UserCreateByAdmin, UserUpdateByAdmin]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        from sqlalchemy import func
        result = await db.execute(
            select(User).filter(func.lower(User.email) == func.lower(email))
        )
        return result.scalars().first()

    async def search_users(self, db: AsyncSession, *, query: str, skip: int = 0, limit: int = 20) -> List[User]:
        result = await db.execute(
            select(User)
            .filter(User.email.ilike(f"%{query}%") | User.full_name.ilike(f"%{query}%"))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

user_repo = UserRepository(User)
