from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import SystemRole

# ==========================================
# 1. BASE SCHEMA (Dùng chung)
# ==========================================
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

# ==========================================
# 2. CREATE SCHEMAS (Tạo tài khoản)
# ==========================================

# Loại 1: Guest tự đăng ký (Tuyệt đối KHÔNG có trường role)
class UserRegister(UserBase):
    """Schema cho Khách tự đăng ký (Sign Up)"""
    password: str = Field(..., min_length=6)
    # Role mặc định sẽ được gán cứng là USER ở tầng logic/database

# Loại 2: Admin tạo tài khoản từ Dashboard
class UserCreateByAdmin(UserBase):
    """Schema cho Admin cấp tài khoản cho người khác"""
    password: str = Field(..., min_length=6)
    # Admin được phép truyền role vào, nếu không truyền sẽ mặc định là USER
    role: SystemRole = SystemRole.USER 

# ==========================================
# 3. UPDATE SCHEMA (Cập nhật thông tin)
# ==========================================
class UserUpdateMe(BaseModel):
    """Schema cho User tự cập nhật Profile. Tuyệt đối không có trường role."""
    full_name: Optional[str] = None
    # Có thể thêm avatar_url, phone_number... nhưng KHÔNG CÓ role

class UserUpdateByAdmin(BaseModel):
    """Schema cho Admin cập nhật thông tin người khác"""
    full_name: Optional[str] = None
    role: Optional[SystemRole] = None # Chỉ Admin mới dùng cái này

# ==========================================
# 4. RESPONSE SCHEMA (Trả dữ liệu về Frontend)
# ==========================================
class UserResponse(UserBase):
    """Schema chuẩn hóa dữ liệu trả về (giấu password đi)"""
    id: UUID
    role: SystemRole
    created_at: datetime

    class Config:
        from_attributes = True # Giúp Pydantic tự động đọc dữ liệu từ model SQLAlchemy

# ==========================================
# 5. AUTH SCHEMAS (Đăng nhập & Token)
# ==========================================
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int

class TokenRefresh(BaseModel):
    refresh_token: str