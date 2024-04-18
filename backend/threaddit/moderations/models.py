from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db

if TYPE_CHECKING:
    from threaddit.threads.models import Thread
    from threaddit.users.models import User


class Role(db.Model):
    __tablename__: str = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)
    user_role: Mapped[list["UserRole"]] = relationship(back_populates="role")


class UserRole(db.Model):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, unique=True)
    thread_id: Mapped[int | None] = mapped_column(ForeignKey("threads.id"), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    user: Mapped["User"] = relationship(back_populates="user_roles")
    role: Mapped["Role"] = relationship(back_populates="user_role")
    thread: Mapped["Thread"] = relationship(back_populates="user_role")

    # noinspection PyTypeChecker
    def __init__(self, user_id: int, role_id: int, thread_id: int | None = None):
        self.user_id = user_id
        self.thread_id = thread_id
        self.role_id = role_id

    @classmethod
    def add_admin(cls, user: "User"):
        db.session.add(UserRole(user_id=user.id, role_id=2))

    @classmethod
    def add_moderator(cls, user: "User", thread: "Thread"):
        db.session.add(UserRole(user_id=user.id, thread_id=thread.id, role_id=1))

    def delete(self):
        db.session.delete(self)
