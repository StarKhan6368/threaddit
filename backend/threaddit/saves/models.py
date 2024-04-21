from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from threaddit import db

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.posts.models import Posts
    from threaddit.threads.models import Thread
    from threaddit.users.models import User


class Saves(db.Model):
    __tablename__ = "saves"
    __table_args__ = (UniqueConstraint("user_id", "post_id", "comment_id", name="unique_save_constraint"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"), nullable=True)
    comment_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=db.func.now())

    # noinspection PyTypeChecker
    def __init__(self, user_id: int, post_id: int | None = None, comment_id: int | None = None):
        self.user_id = user_id
        self.post_id = post_id
        self.comment_id = comment_id

    @staticmethod
    def add(user: "User", post: "Posts", comment: "Comments|None" = None):
        new_save = Saves(user_id=user.id, post_id=post.id)
        if comment:
            comment.saved_count += 1
            new_save.comment_id = comment.id
        else:
            post.saved_count += 1
        db.session.add(new_save)

    def delete(self, post: "Posts", comment: "Comments|None" = None):
        if comment:
            comment.saved_count -= 1
        else:
            post.saved_count -= 1
        db.session.delete(self)

    @staticmethod
    def get_save(user: "User", thread: "Thread", post: "Posts", comment: "Comments|None" = None):
        if comment:
            comment.validate_comment(thread, post)
        else:
            post.validate_post(thread)
        comment_id = comment.id if comment else None

        return db.session.scalar(
            sa.select(Saves).where(
                Saves.comment_id == comment_id,
                Saves.post_id == post.id,
                Saves.user_id == user.id,
            )
        )
