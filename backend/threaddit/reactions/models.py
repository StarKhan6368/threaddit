from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.posts.models import Posts
    from threaddit.users.models import User


class Reactions(db.Model):
    __tablename__ = "reactions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"))
    comment_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    is_upvote: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=db.func.now(), nullable=False)
    user: Mapped["User"] = relationship(back_populates="reaction")
    post: Mapped["Posts"] = relationship(back_populates="reaction")
    comment: Mapped["Comments"] = relationship(back_populates="reaction")

    def __init__(self, user_id: int, is_upvote: bool, post_id: int | None = None, comment_id: int | None = None):
        self.user_id = user_id
        self.post_id = post_id
        self.comment_id = comment_id
        self.is_upvote = is_upvote

    @classmethod
    def add(cls, user_id: int, is_upvote: bool, post: "Posts | None" = None, comment: "Comments | None" = None):
        value = 1 if is_upvote else -1
        if post:
            post.karma_count += value
            post.user.post_karma += value
            new_reaction = Reactions(user_id=user_id, is_upvote=is_upvote, post_id=post.id)
            db.session.add(new_reaction)
        elif comment:
            comment.user.comment_karma += value
            comment.karma_count += value
            new_reaction = Reactions(user_id=user_id, is_upvote=is_upvote, comment_id=comment.id)
            db.session.add(new_reaction)
        db.session.commit()

    def patch(self, is_upvote: bool):
        value = 2 if is_upvote else -2
        if post := self.post:
            post.user.post_karma += value
            post.karma_count += value
        elif comment := self.comment:
            comment.user.comment_karma += value
            comment.karma_count += value
        self.is_upvote = is_upvote
        db.session.commit()

    def remove(self):
        value = -1 if self.is_upvote else 1
        if self.post:
            self.post.user.post_karma += value
            self.post.karma_count += value
        elif self.comment:
            self.comment.user.comment_karma += value
            self.comment.karma_count += value
        db.session.delete(self)
        db.session.commit()

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "comment_id": self.comment_id,
            "is_upvote": self.is_upvote,
            "created_at": self.created_at,
        }
