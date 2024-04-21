import enum
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit import db

if TYPE_CHECKING:
    from threaddit.media.models import Media
    from threaddit.users.models import User


class NotifType(enum.Enum):
    # Thread Notifications
    THREAD_JOINED = "THREAD_JOINED"
    # Post Notifications
    POST_COMMENT = "POST_COMMENT"
    POST_UPVOTED = "POST_UPVOTED"
    POST_DOWNVOTED = "POST_DOWNVOTED"
    POST_REMOVED = "POST_REMOVED"
    POST_LOCKED = "POST_LOCKED"
    POST_UNLOCKED = "POST_UNLOCKED"
    POST_REPORTED = "POST_REPORTED"
    # Comment Notifications
    COMMENT_REPLY = "COMMENT_REPLY"
    COMMENT_UPVOTED = "COMMENT_UPVOTED"
    COMMENT_DOWNVOTED = "COMMENT_DOWNVOTED"
    COMMENT_REMOVED = "COMMENT_REMOVED"
    COMMENT_LOCKED = "COMMENT_LOCKED"
    COMMENT_UNLOCKED = "COMMENT_UNLOCKED"
    COMMENT_REPORTED = "COMMENT_REPORTED"
    # Message Notifications
    NEW_MESSAGE = "NEW_MESSAGE"
    # Report Notifications
    REPORT_RESOLVED = "REPORT_RESOLVED"
    REPORT_REJECTED = "REPORT_REJECTED"
    # Moderator Notifications
    MODERATOR_INVITED = "MODERATOR_INVITED"
    MODINV_ACCEPTED = "MODERATOR_ACCEPTED"
    MODERATOR_ADDED = "MODERATOR_ADDED"
    MODINV_REJECTED = "MODERATOR_REJECTED"
    MODERATOR_REMOVED = "MODERATOR_REMOVED"
    # Admin Notifications
    ADMIN_INVITED = "ADMIN_INVITED"
    ADMIN_ADDED = "ADMIN_ADDED"
    ADMINV_ACCEPTED = "ADMIN_ACCEPTED"
    ADMINV_REJECTED = "ADMIN_REJECTED"
    ADMIN_REMOVED = "ADMIN_REMOVED"


class Notifications(db.Model):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    notif_type: Mapped[NotifType] = mapped_column(ENUM(NotifType, name="notif_type_enum"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(nullable=True)
    sub_title: Mapped[str | None] = mapped_column(nullable=True)
    content: Mapped[str] = mapped_column(nullable=False)
    res_id: Mapped[int | None] = mapped_column(nullable=True)
    res_media_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(tz=UTC), nullable=False)
    seen_at: Mapped[datetime | None] = mapped_column(nullable=True)
    user: Mapped["User"] = relationship(back_populates="notifications")
    media: Mapped["Media"] = relationship()

    # noinspection PyTypeChecker
    def __init__(
        self,
        notif_type: NotifType,
        user_id: int,
        title: str,
        sub_title: str | None = None,
        content: str | None = None,
        res_id: int | None = None,
        res_media_id: int | None = None,
    ):
        self.user_id = user_id
        self.notif_type = notif_type
        self.title = title
        self.sub_title = sub_title
        self.content = content
        self.res_id = res_id
        self.res_media_id = res_media_id

    @staticmethod
    def notify(
        notif_type: NotifType,
        user: "User|int",
        title: str,
        sub_title: str | None = None,
        content: str | None = None,
        res_id: int | None = None,
        res_media_id: int | None = None,
    ):
        new_notif = Notifications(
            notif_type=notif_type,
            user_id=user if isinstance(user, int) else user.id,
            title=title,
            sub_title=sub_title,
            content=content,
            res_id=res_id,
            res_media_id=res_media_id,
        )
        db.session.add(new_notif)
        return new_notif

    @staticmethod
    def notify_bulk(
        notify_type: NotifType,
        users: list[int],
        title: str,
        sub_title: str | None = None,
        content: str | None = None,
        res_id: int | None = None,
        res_media_id: int | None = None,
    ):
        db.session.bulk_insert_mappings(
            Notifications,
            [
                {
                    "notif_type": notify_type,
                    "user_id": user,
                    "title": title,
                    "sub_title": sub_title,
                    "content": content,
                    "res_id": res_id,
                    "res_media_id": res_media_id,
                }
                for user in users
            ],
        )

    def read(self):
        # noinspection PyTypeChecker
        self.seen_at = datetime.now(tz=UTC)

    def delete(self):
        db.session.delete(self)

    def __str__(self):
        return (
            f"<Notifications {self.id} type={self.notif_type} user={self.user_id}"
            f" res={self.res_id} media={self.res_media_id}>"
        )
