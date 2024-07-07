from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import TEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit import db
from threaddit.message.schemas import MESSAGE_CONTENT_REGEX

if TYPE_CHECKING:
    from threaddit.media.models import Media
    from threaddit.user.models import Users


class Messages(db.Model):
    """Database model for messages table."""

    # Table Metadata
    __tablename__ = "messages"
    __table_args__ = (
        CheckConstraint(rf"encrypted_content ~* '{MESSAGE_CONTENT_REGEX.pattern}'"),
        CheckConstraint("num_nonnulls(encrypted_content, media_id) >= 1"),
        Index(None, "sender_id", "receiver_id"),
    )

    # Table Columns
    message_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    media_id: Mapped[int | None] = mapped_column(
        ForeignKey("media.media_id", ondelete="set null", onupdate="cascade"), nullable=True
    )
    encrypted_content: Mapped[str] = mapped_column(TEXT, nullable=False)
    created_on: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    seen_at: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    updated_on: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())

    # Relationships
    sender: Mapped["Users"] = relationship("Users", foreign_keys=[sender_id], lazy="raise", uselist=False)
    receiver: Mapped["Users"] = relationship("Users", foreign_keys=[receiver_id], lazy="raise", uselist=False)
    media: Mapped["Media | None"] = relationship("Media", foreign_keys=[media_id], lazy="joined", uselist=False)
