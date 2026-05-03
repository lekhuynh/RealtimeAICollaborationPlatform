from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserRegister, UserCreateByAdmin
from app.repositories.user_repo import user_repo
from app.utils.security import hash_password

class UserService:
    async def create_user(self, db: AsyncSession, user_in: UserRegister) -> User:
        user_data = user_in.model_dump()
        user_data["password_hash"] = hash_password(user_data.pop("password"))
        db_user = User(**user_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        return await user_repo.get_by_email(db, email=email)

    async def get_user(self, db: AsyncSession, user_id: str) -> Optional[User]:
        return await user_repo.get(db, id=user_id)

    async def update_user(self, db: AsyncSession, *, db_obj: User, obj_in: dict) -> User:
        return await user_repo.update(db, db_obj=db_obj, obj_in=obj_in)
        
    async def search_users(self, db: AsyncSession, *, query: str) -> List[User]:
        return await user_repo.search_users(db, query=query)

user_service = UserService()
