from app.models.enums import DocumentRole, DocumentPermission


ROLE_PERMISSIONS = {
    DocumentRole.OWNER: set(DocumentPermission),

    DocumentRole.EDITOR: {
        DocumentPermission.READ_DOCUMENT,
        DocumentPermission.EDIT_DOCUMENT,
        DocumentPermission.SEND_MESSAGE,
        DocumentPermission.USE_AI,
    },

    DocumentRole.VIEWER: {
        DocumentPermission.READ_DOCUMENT,
    },
}


def has_permission(role: DocumentRole, permission: DocumentPermission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())

import uuid
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select # Cần import thêm cái này cho Async
from app.db.session import get_db
from app.utils.security import get_current_user 
from app.models.document_member import DocumentMember
from app.models.user import User

class RequireDocPermission:
    def __init__(self, required_permission: DocumentPermission):
        self.required_permission = required_permission

    # 1. HÀM NÀY PHẢI LÀ ASYNC
    async def __call__(
        self, 
        document_id: str, 
        db: AsyncSession = Depends(get_db),  # 2. DÙNG ASYNCSESSION
        current_user: User = Depends(get_current_user)
    ):
        # 3. TRUY VẤN ASYNC CHUẨN SQLALCHEMY 2.0
        stmt = select(DocumentMember).filter(
            DocumentMember.document_id == document_id,
            DocumentMember.user_id == current_user.id
        )
        
        # Chờ database trả kết quả về
        result = await db.execute(stmt)
        # Lấy ra record đầu tiên
        member = result.scalars().first()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Bạn chưa được mời vào tài liệu này."
            )

        if not has_permission(member.role, self.required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail=f"Tài khoản của bạn không có quyền: {self.required_permission.value}"
            )

        return member

from app.models.enums import SystemRole

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != SystemRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin privileges"
        )
    return current_user