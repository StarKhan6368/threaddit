from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask_jwt_extended import current_user
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db
from threaddit.media.models import Media, OpType

if TYPE_CHECKING:
    from threaddit.media.schemas import MediaFormType
    from threaddit.moderations.models import UserRole
    from threaddit.posts.models import Posts
    from threaddit.threads.schemas import ThreadFormType
    from threaddit.users.models import User


class Thread(db.Model):
    __tablename__ = "threads"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=sa.func.now())
    logo_id: Mapped[int] = mapped_column(ForeignKey("media.id"), nullable=True)
    banner_id: Mapped[int] = mapped_column(ForeignKey("media.id"), nullable=True)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rules: Mapped[str | None] = mapped_column(nullable=True)
    join_message: Mapped[str | None] = mapped_column(nullable=True)
    post_count: Mapped[int] = mapped_column(default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(default=0, nullable=False)
    subscriber_count: Mapped[int] = mapped_column(default=0, nullable=False)
    user: Mapped["User"] = relationship(back_populates="thread")
    subscription: Mapped[list["Subscription"]] = relationship(back_populates="thread")
    post: Mapped[list["Posts"]] = relationship(back_populates="thread")
    logo: Mapped["Media"] = relationship(foreign_keys=[logo_id])
    banner: Mapped["Media"] = relationship(foreign_keys=[banner_id])
    user_role: Mapped[list["UserRole"]] = relationship(back_populates="thread")

    @property
    def is_subscribed(self):
        if not current_user:
            return False
        subscription = db.session.scalar(
            sa.select(Subscription).where(Subscription.user_id == current_user.id, Subscription.thread_id == self.id)
        )
        return subscription is not None

    # noinspection PyTypeChecker
    def __init__(self, name: str, created_by: int, description: str | None = None):
        self.name = name
        self.description = description
        self.created_by = created_by

    @classmethod
    def add(cls, form: "ThreadFormType", user: "User"):
        new_sub = Thread(
            name=form["name"],
            description=form["description"],
            created_by=user.id,
        )
        db.session.add(new_sub)
        new_sub.update(form)
        return new_sub

    def update(self, form: "ThreadFormType"):
        if form["logo"]:
            self.logo = self._handle_media(self.logo, form["logo"])
        if form["banner"]:
            self.banner = self._handle_media(self.banner, form["banner"])
        self.description = form["description"] or self.description
        self.rules = form["rules"] or self.rules
        self.join_message = form["join_message"] or self.join_message

    def _handle_media(self, media: "Media | None", form: "MediaFormType"):
        if media and form["media_id"] and media.id == form["media_id"].id:
            match form["operation"]:
                case OpType.UPDATE:
                    media.update(f"threads/{self.name}", form=form)
                case OpType.DELETE:
                    media.delete()
        elif not form["media_id"] and form["operation"] == OpType.ADD and not media:
            media = Media.add(f"threads/{self.name}", form=form)
        return media


class Subscription(db.Model):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    thread_id: Mapped[int] = mapped_column(ForeignKey("threads.id"))
    user: Mapped["User"] = relationship(back_populates="subscriptions")
    thread: Mapped["Thread"] = relationship(back_populates="subscription")

    @classmethod
    def add(cls, user: "User", thread: "Thread"):
        new_sub = Subscription(user_id=user.id, thread_id=thread.id)
        thread.subscriber_count += 1
        db.session.add(new_sub)

    def delete(self, thread: "Thread"):
        thread.subscriber_count -= 1
        db.session.delete(self)

    # noinspection PyTypeChecker
    def __init__(self, user_id: int, thread_id: int):
        self.user_id = user_id
        self.thread_id = thread_id
