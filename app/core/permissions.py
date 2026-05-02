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