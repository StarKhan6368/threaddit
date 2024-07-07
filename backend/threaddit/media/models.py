import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, func
from sqlalchemy.dialects.postgresql import ENUM, TEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import false

from threaddit import db
from threaddit.media.schemas import FILE_NAME_REGEX, MEDIA_URL_REGEX

if TYPE_CHECKING:
    from threaddit.user.models import Users


class MediaType(enum.Enum):
    """Enum for media type."""

    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    URL = "URL"


class Media(db.Model):
    """Database model for media table."""

    # Table Metadata
    __tablename__ = "media"
    __table_args__ = (
        CheckConstraint(rf"name ~* '{FILE_NAME_REGEX.pattern}'"),
        CheckConstraint(f"url ~* '{MEDIA_URL_REGEX.pattern}'"),
    )

    # Table Columns
    media_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    media_type: Mapped[MediaType] = mapped_column(ENUM(MediaType, name="MediaType"), nullable=False)
    url: Mapped[str] = mapped_column(TEXT, nullable=False)
    cldr_id: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    is_nsfw: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_spoiler: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    created_on: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_on: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())

    # Table Relations
    creator: Mapped["Users"] = relationship("Users", foreign_keys=[creator_id], lazy="raise", uselist=False)
