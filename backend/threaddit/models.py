from datetime import datetime

from flask import jsonify
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey
from typing_extensions import TYPE_CHECKING

from threaddit import db

if TYPE_CHECKING:
    from threaddit.subthreads.models import Subthread
    from threaddit.users.models import User


class Role(db.Model):
    __tablename__: str = "roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    slug: Mapped[str] = mapped_column(unique=True, nullable=False)
    user_role: Mapped[list["UserRole"]] = relationship(back_populates="role")


class UserRole(db.Model):
    __tablename__ = "user_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False, primary_key=True)
    subthread_id: Mapped[int | None] = mapped_column(ForeignKey("subthreads.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    user: Mapped["User"] = relationship(back_populates="user_role")
    role: Mapped["Role"] = relationship(back_populates="user_role")
    subthread: Mapped["Subthread"] = relationship(back_populates="user_role")

    def __init__(self, user_id: int, subthread_id: int, role_id: int):
        self.user_id = user_id
        self.subthread_id = subthread_id
        self.role_id = role_id

    @classmethod
    def add_moderator(cls, user_id: int, subthread_id: int):
        check_mod = UserRole.query.filter_by(user_id=user_id, subthread_id=subthread_id, role_id=1).first()
        if check_mod:
            return jsonify({"message": "Moderator already exists"}), 400
        new_mod = UserRole(user_id=user_id, subthread_id=subthread_id, role_id=1)
        db.session.add(new_mod)
        db.session.commit()

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "subthread_id": self.subthread_id,
        }
