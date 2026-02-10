from datetime import datetime
from enum import Enum as PyEnum

from app.config.database import Base
from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


class RoleType(str, PyEnum):
    ADMIN = "Admin"
    USER = "User"
    MODERATOR = "Moderator"


class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[RoleType] = mapped_column(Enum(RoleType), nullable=False)
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user = relationship("User", back_populates="roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
