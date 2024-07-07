import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from threaddit import db

if TYPE_CHECKING:
    from threaddit.comment.models import Comments
    from threaddit.post.models import Posts
    from threaddit.user.models import Users


class VoteType(enum.Enum):
    """Enum for vote types."""

    UPVOTE = "UPVOTE"
    DOWNVOTE = "DOWNVOTE"


class Votes(db.Model):
    """Database model for votes."""

    # Table Metadata
    __tablename__ = "votes"
    __table_args__ = (Index(None, "post_id", "creator_id", "comment_id", unique=True),)

    # Table Columns
    vote_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.post_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.comment_id", ondelete="restrict", onupdate="cascade"), nullable=True
    )
    vote_type: Mapped[VoteType] = mapped_column(ENUM(VoteType, name="VoteType"), nullable=False)
    created_on: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_on: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())

    # Table Relations
    creator: Mapped["Users"] = relationship("Users", foreign_keys=[creator_id], lazy="raise", uselist=False)
    post: Mapped["Posts"] = relationship("Posts", foreign_keys=[post_id], lazy="raise", uselist=False)
    comment: Mapped["Comments"] = relationship("Comments", foreign_keys=[comment_id], lazy="raise", uselist=False)
