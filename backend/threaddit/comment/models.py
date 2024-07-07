from datetime import datetime
from typing import TYPE_CHECKING

from flask_sqlalchemy.query import Query
from sqlalchemy import CheckConstraint, ForeignKey, Index, false, func
from sqlalchemy.dialects.postgresql import TEXT, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils import TSVectorType

from threaddit import db
from threaddit.comment.schemas import COMMENT_CONTENT_REGEX

if TYPE_CHECKING:
    from threaddit.media.models import Media
    from threaddit.post.models import Posts
    from threaddit.thread.models import Threads
    from threaddit.user.models import Users


class CommentQueryMixin(Query, SearchQueryMixin):
    """Mixin for adding search functionality to Comments model."""


class Comments(db.Model):
    """Database model for comments table."""

    # Table Metadata
    __tablename__ = "comments"
    __table_args__ = (
        CheckConstraint(f"content ~* '{COMMENT_CONTENT_REGEX.pattern}'"),
        CheckConstraint("num_nonnulls(content, media_id) >= 1"),
        Index(None, "thread_id", "post_id", "comment_id", unique=True),
    )
    query_class = CommentQueryMixin

    # Table Columns
    comment_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    thread_id: Mapped[int] = mapped_column(
        ForeignKey("threads.thread_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    post_id: Mapped[int | None] = mapped_column(
        ForeignKey("posts.post_id", ondelete="restrict", onupdate="cascade"), nullable=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.comment_id", ondelete="restrict", onupdate="cascade")
    )
    content: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    media_id: Mapped[int | None] = mapped_column(
        ForeignKey("media.media_id", ondelete="set null", onupdate="cascade"), nullable=True
    )
    upvote_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    downvote_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    replies_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    save_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    report_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    depth: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    is_nsfw: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_spoiler: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_sticky: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_removed: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_locked: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    created_on: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_on: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())
    search_vector: Mapped[TSVectorType] = mapped_column(TSVectorType("content"), nullable=False)

    # Table Relations
    creator: Mapped["Users"] = relationship("Users", foreign_keys=[creator_id], lazy="raise", uselist=False)
    thread: Mapped["Threads"] = relationship("Threads", foreign_keys=[thread_id], lazy="raise", uselist=False)
    post: Mapped["Posts"] = relationship("Posts", foreign_keys=[post_id], lazy="raise", uselist=False)
    parent: Mapped["Comments"] = relationship(
        "Comments", foreign_keys=[parent_id], lazy="raise", uselist=False, viewonly=True
    )
    media: Mapped["Media"] = relationship("Media", foreign_keys=[media_id], lazy="raise", uselist=False)
    replies: Mapped[list["Comments"]] = relationship(
        "Comments", foreign_keys=[parent_id], lazy="raise", uselist=True, viewonly=True
    )
