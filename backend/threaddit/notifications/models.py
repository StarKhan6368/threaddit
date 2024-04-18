import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit import db

if TYPE_CHECKING:
    from threaddit.users.models import User


class NotifType(enum.Enum):
    THREAD_JOINED = "THREAD_JOINED"
    THREAD_UPDATED = "THREAD_UPDATED"
    REPORT_SUBMITTED = "REPORT_SUBMITTED"
    REPORT_RESOLVED = "REPORT_RESOLVED"
    POST_REMOVED = "POST_REMOVED"
    POST_COMMENT = "POST_COMMENT"
    POST_UPVOTED = "POST_UPVOTED"
    COMMENT_REMOVED = "COMMENT_REMOVED"
    COMMENT_REPLY = "COMMENT_REPLY"
    COMMENT_UPVOTED = "COMMENT_UPVOTED"
    MESSAGE_ARRIVED = "MESSAGE_ARRIVED"
    MODERATOR_ADDED = "MODERATOR_ADDED"
    MODERATOR_REMOVED = "MODERATOR_REMOVED"


class Notifications(db.Model):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    notif_type: Mapped[NotifType] = mapped_column(ENUM(NotifType, name="notif_type_enum"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=db.func.now(), nullable=False)
    seen_at: Mapped[datetime | None] = mapped_column(nullable=True)
    user: Mapped["User"] = relationship(back_populates="notifications")
