from datetime import datetime
from typing import TYPE_CHECKING

from flask_sqlalchemy.query import Query
from sqlalchemy import CheckConstraint, ForeignKey, Index, false, func
from sqlalchemy.dialects.postgresql import ARRAY, TEXT, TIMESTAMP, VARCHAR
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType

from threaddit import db
from threaddit.post.schemas import POST_TITLE_REGEX

if TYPE_CHECKING:
    from threaddit.media.models import Media
    from threaddit.thread.models import Threads
    from threaddit.user.models import Users


class PostQuery(Query, SearchQueryMixin):
    """Mixin for adding search functionality to Posts model."""


class Posts(db.Model):
    """Database model for posts table."""

    # Table Metadata
    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint(f"title ~* '{POST_TITLE_REGEX.pattern}'"),
        CheckConstraint("array_ndims(flairs) = 1 AND array_length(flairs, 1) <= 4"),
        Index(None, "thread_id", "post_id", unique=True),
    )
    query_class = PostQuery

    # Table Columns
    post_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    thread_id: Mapped[int] = mapped_column(
        ForeignKey("threads.thread_id", ondelete="restrict", onupdate="cascade"), nullable=False
    )
    title: Mapped[str] = mapped_column(VARCHAR(126), nullable=False)
    content: Mapped[str] = mapped_column(TEXT)
    upvote_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    downvote_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    comment_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    save_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    report_count: Mapped[int] = mapped_column(nullable=False, default=0, server_default="0")
    is_nsfw: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_spoiler: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_sticky: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_deleted: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_removed: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    is_locked: Mapped[bool] = mapped_column(nullable=False, default=False, server_default=false())
    flairs: Mapped[list[str]] = mapped_column(
        ARRAY(VARCHAR(16), zero_indexes=True), nullable=False, server_default="{}"
    )
    search_vector: Mapped[TSVectorType] = mapped_column(TSVectorType("title", "content"), nullable=False)
    created_on: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_on: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=True), nullable=True, onupdate=func.now())

    # Table Relationships
    creator: Mapped["Users"] = relationship("Users", foreign_keys=[creator_id], lazy="raise", uselist=False)
    thread: Mapped["Threads"] = relationship("Threads", foreign_keys=[thread_id], lazy="raise", uselist=False)
    media_list: AssociationProxy[list["Media"]] = association_proxy("post_media", "media")


class PostMedia(db.Model):
    """Database Model for Many-to-Many between Posts and Media."""

    # Table Metadata
    __tablename__ = "post_media"

    # Table Columns
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.post_id", ondelete="cascade", onupdate="cascade"), primary_key=True, nullable=False
    )
    media_id: Mapped[int] = mapped_column(
        ForeignKey("media.media_id", ondelete="cascade", onupdate="cascade"), primary_key=True, nullable=False
    )

    # Table Relationships
    post: Mapped["Posts"] = relationship("Posts", foreign_keys=[post_id], lazy="raise", uselist=False)
    media: Mapped["Media"] = relationship("Media", foreign_keys=[media_id], lazy="raise", uselist=False)
