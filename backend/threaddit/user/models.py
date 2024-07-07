from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, false, func
from sqlalchemy.dialects.postgresql import TEXT, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit.user.schemas import USER_EMAIL_REGEX, USER_NAME_REGEX

if TYPE_CHECKING:
    from threaddit.media.models import Media

from threaddit import db


class Users(db.Model):
    """Database model for users table."""

    # Table Metadata
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(f"name ~* '{USER_NAME_REGEX.pattern}'"),
        CheckConstraint(f"email ~* '{USER_EMAIL_REGEX.pattern}'"),
    )

    # Table Columns
    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(32), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(TEXT, nullable=False)
    bio: Mapped[str | None] = mapped_column(VARCHAR(256), nullable=True)
    avatar_id: Mapped[int | None] = mapped_column(
        ForeignKey("media.media_id", ondelete="set null", onupdate="cascade"), nullable=True
    )
    banner_id: Mapped[int | None] = mapped_column(
        ForeignKey("media.media_id", ondelete="set null", onupdate="cascade"), nullable=True
    )
    is_nsfw: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    post_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    post_karma: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    comment_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    comment_karma: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    last_seen: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    created_on: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_on: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())

    # Table Relations
    avatar: Mapped["Media | None"] = relationship("Media", foreign_keys=[avatar_id], lazy="joined", uselist=False)
    banner: Mapped["Media | None"] = relationship("Media", foreign_keys=[banner_id], lazy="joined", uselist=False)
