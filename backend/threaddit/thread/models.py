from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, false, func
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, TIMESTAMP, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit import db
from threaddit.thread.schemas import THREAD_NAME_REGEX

if TYPE_CHECKING:
    from threaddit.media.models import Media
    from threaddit.user.models import Users


class Threads(db.Model):
    """Database model for threads table."""

    # Table Metadata
    __tablename__ = "threads"
    __table_args__ = (
        CheckConstraint(f"name ~* '{THREAD_NAME_REGEX.pattern}'"),
        CheckConstraint("array_ndims(flairs) = 1 AND array_length(flairs, 1) <= 16"),
    )

    # Table Columns
    thread_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(VARCHAR(16), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    flairs: Mapped[list[str]] = mapped_column(
        ARRAY(VARCHAR(16), zero_indexes=True), nullable=False, server_default="{}"
    )
    join_message: Mapped[str] = mapped_column(
        VARCHAR(256), nullable=False, server_default="Welcome to the Thread, Check the rules."
    )
    post_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    comment_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    subscription_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    is_locked: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_nsfw: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_banned: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_private: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    logo_id: Mapped[int | None] = mapped_column(
        ForeignKey("media.media_id", ondelete="set null", onupdate="cascade"), nullable=True
    )
    banner_id: Mapped[int | None] = mapped_column(
        ForeignKey("media.media_id", ondelete="set null", onupdate="cascade"), nullable=True
    )
    created_on: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_on: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())

    # Table Relationships
    creator: Mapped["Users"] = relationship("Users", foreign_keys=[creator_id], lazy="raise", uselist=False)
    logo: Mapped["Media | None"] = relationship("Media", foreign_keys=[logo_id], lazy="joined", uselist=False)
    banner: Mapped["Media | None"] = relationship("Media", foreign_keys=[banner_id], lazy="joined", uselist=False)
