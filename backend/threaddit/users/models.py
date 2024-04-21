from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from threaddit import db, jwt
from threaddit.media.models import Media, OpType
from threaddit.moderations.models import RoleType

if TYPE_CHECKING:
    from threaddit.auth.models import TokenBlockList
    from threaddit.comments.models import Comments
    from threaddit.moderations.models import UserRole
    from threaddit.notifications.models import Notifications
    from threaddit.posts.models import Posts
    from threaddit.reactions.models import Reactions
    from threaddit.reports.models import Reports
    from threaddit.threads.models import Subscription, Thread
    from threaddit.users.schemas import UserFormType


class User(db.Model):
    __tablename__: str = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    bio: Mapped[str | None] = mapped_column(nullable=True)
    post_karma: Mapped[int] = mapped_column(default=0, nullable=False)
    comment_karma: Mapped[int] = mapped_column(default=0, nullable=False)
    post_count: Mapped[int] = mapped_column(default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(default=0, nullable=False)
    registration_date: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    avatar_id: Mapped[int] = mapped_column(ForeignKey("media.id"), nullable=True)
    thread: Mapped[list["Thread"]] = relationship(back_populates="creator")
    blacklist_tokens: Mapped[list["TokenBlockList"]] = relationship(back_populates="user")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    posts: Mapped[list["Posts"]] = relationship(back_populates="user")
    roles_accepted: Mapped[list["UserRole"]] = relationship(
        back_populates="grantee", foreign_keys="UserRole.grantee_id"
    )
    roles_granted: Mapped[list["UserRole"]] = relationship(back_populates="granter", foreign_keys="UserRole.granter_id")
    comments: Mapped[list["Comments"]] = relationship(back_populates="user")
    reactions: Mapped[list["Reactions"]] = relationship(back_populates="user")
    media: Mapped["Media"] = relationship()
    notifications: Mapped[list["Notifications"]] = relationship(back_populates="user")
    reports: Mapped[list["Reports"]] = relationship(back_populates="user")

    # noinspection PyTypeChecker
    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password_hash)

    @staticmethod
    def add(username: str, email: str, password_hash: str):
        user = User(username, email, password_hash)
        db.session.add(user)
        return user

    # noinspection DuplicatedCode
    def update(self, form: "UserFormType"):
        if form["media_id"] and self.avatar_id == form["media_id"].id:
            match form["operation"]:
                case OpType.UPDATE:
                    self.media.update(f"users/{self.username}", form=form)
                case OpType.DELETE:
                    self.media.delete()
        elif not form["media_id"] and form["operation"] == OpType.ADD and not self.avatar_id:
            self.media = Media.add(f"users/{self.username}", form=form)
        self.bio = form["bio"] or self.bio

    @property
    def rolenames(self) -> set["RoleType"]:
        return {role.role_type.name for role in self.roles_accepted}

    @property
    def is_admin(self):
        return RoleType.ADMIN in self.rolenames

    def moderator_in(self, thread: "Thread"):
        return thread.id in self.modlist

    @property
    def modlist(self) -> list[int]:
        return [role.thread_id for role in self.roles_accepted if role.role_type == RoleType.MODERATOR]

    def check_password(self, password: str):
        return check_password_hash(self.password_hash, password)


@jwt.user_identity_loader
def user_identity_lookup(user_id: int) -> int | None:
    user = db.session.scalar(sa.select(User).where(User.id == user_id))
    return user.id if user else None


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return db.session.scalar(sa.select(User).where(User.id == identity))
