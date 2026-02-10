from enum import Enum as PyEnum


class RoleType(str, PyEnum):
    ADMIN = "Admin"
    USER = "User"
    MODERATOR = "Moderator"
