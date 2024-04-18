from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.posts.models import Posts
    from threaddit.users.models import User


class Reactions(db.Model):
    __tablename__ = "reactions"
    __tableargs__ = UniqueConstraint(
        "user_id", "post_id", "comment_id", name="reactions_user_id_post_id_comment_id_key"
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int | None] = mapped_column(ForeignKey("posts.id"))
    comment_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    is_upvote: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=db.func.now(), nullable=False)
    user: Mapped["User"] = relationship(back_populates="reactions")
    post: Mapped["Posts"] = relationship(back_populates="reaction")
    comment: Mapped["Comments"] = relationship(back_populates="reaction")

    # noinspection PyTypeChecker
    def __init__(self, user_id: int, is_upvote: bool, post_id: int, comment_id: int | None = None):
        self.user_id = user_id
        self.post_id = post_id
        self.comment_id = comment_id
        self.is_upvote = is_upvote

    @classmethod
    def add(cls, is_upvote: bool, user: "User", post: "Posts", comment: "Comments | None" = None):
        new_reaction = Reactions(user_id=user.id, is_upvote=is_upvote, post_id=post.id)
        if comment:
            new_reaction.comment_id = comment.id
        Reactions.handle_vote(1 if is_upvote else -1, is_upvote, post, comment)
        db.session.add(new_reaction)

    def update(self, is_upvote: bool, post: "Posts", comment: "Comments | None" = None):
        Reactions.handle_vote(2 if self.is_upvote else -2, is_upvote, post, comment)
        # noinspection PyTypeChecker
        self.is_upvote = is_upvote

    def delete(self, post: "Posts", comment: "Comments | None" = None):
        Reactions.handle_vote(-1, False, post, comment)  # noqa: FBT003
        db.session.delete(self)

    @staticmethod
    def handle_vote(value: int, is_upvote: bool, post: "Posts", comment: "Comments | None" = None):
        if comment:
            comment.user.comment_karma += value
            if is_upvote:
                comment.upvotes += 1
            else:
                comment.downvotes += 1
        else:
            post.user.post_karma += value
            if is_upvote:
                post.upvotes += 1
            else:
                post.downvotes += 1
