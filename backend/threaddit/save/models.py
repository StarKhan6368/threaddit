from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit import db

if TYPE_CHECKING:
    from threaddit.comment.models import Comments
    from threaddit.post.models import Posts
    from threaddit.user.models import Users


class Saves(db.Model):
    """Database model for Post and Comment saves."""

    # Table Metadata
    __tablename__ = "saves"
    __table_args__ = (Index(None, "creator_id", "post_id", "comment_id", unique=True),)

    # Table Columns
    save_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.post_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.comment_id", ondelete="restrict", onupdate="cascade"), nullable=True
    )
    created_on: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    # Table Relationships
    creator: Mapped["Users"] = relationship("Users", foreign_keys=[creator_id], lazy="raise", uselist=False)
    post: Mapped["Posts"] = relationship("Posts", foreign_keys=[post_id], lazy="raise", uselist=False)
    comment: Mapped["Comments"] = relationship("Comments", foreign_keys=[comment_id], lazy="raise", uselist=False)
