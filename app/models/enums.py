from enum import StrEnum


class SystemRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class SystemPermission(StrEnum):
    MANAGE_USERS = "manage_users"
    VIEW_ALL_DOCUMENTS = "view_all_documents"
    DELETE_ANY_DOCUMENT = "delete_any_document"
    BAN_USER = "ban_user"


class DocumentRole(StrEnum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"


class DocumentPermission(StrEnum):
    # document
    READ_DOCUMENT = "read_document"
    EDIT_DOCUMENT = "edit_document"
    DELETE_DOCUMENT = "delete_document"

    # member
    MANAGE_MEMBERS = "manage_members"
    INVITE_MEMBER = "invite_member"
    REMOVE_MEMBER = "remove_member"

    # chat
    SEND_MESSAGE = "send_message"
    DELETE_MESSAGE = "delete_message"

    # AI
    USE_AI = "use_ai"
    BROADCAST_AI = "broadcast_ai"