from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.utils.security import get_current_user
from typing import List
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateMe
from app.services.user_service import user_service

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current logged in user.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_me(user_in: UserUpdateMe, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = await user_service.update_user(db, db_obj=current_user, obj_in=user_in.model_dump(exclude_unset=True))
    return user

@router.get("/search", response_model=List[UserResponse])
async def search_users(q: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await user_service.search_users(db, query=q)

@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(user_id: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = await user_service.get_user(db, user_id=user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="User not found")
    return user
