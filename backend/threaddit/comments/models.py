from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db
from threaddit.media.models import Media, OpType

if TYPE_CHECKING:
    from threaddit.comments.schemas import CommentBodyType
    from threaddit.posts.models import Posts
    from threaddit.reactions.models import Reactions
    from threaddit.threads.models import Thread
    from threaddit.users.models import User


class Comments(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"), nullable=True)
    edited_at: Mapped[datetime] = mapped_column(nullable=True)
    content: Mapped[str] = mapped_column(nullable=True)
    media_id: Mapped[int | None] = mapped_column(ForeignKey("media.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=db.func.now(), nullable=False)
    upvotes: Mapped[int] = mapped_column(default=0, nullable=False)
    downvotes: Mapped[int] = mapped_column(default=0, nullable=False)
    saved_count: Mapped[int] = mapped_column(default=0)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    replies_count: Mapped[int] = mapped_column(default=0, nullable=False)
    reaction: Mapped[list["Reactions"]] = relationship(back_populates="comment")
    media: Mapped["Media"] = relationship()
    user: Mapped["User"] = relationship(back_populates="comments")
    post: Mapped["Posts"] = relationship(back_populates="comment")
    parent: Mapped["Comments"] = relationship(back_populates="children", remote_side="Comments.id")
    children: Mapped[list["Comments"]] = relationship(back_populates="parent", foreign_keys="Comments.parent_id")

    @hybrid_property
    def karma(self) -> int:
        return self.upvotes - self.downvotes

    @classmethod
    @karma.expression
    def karma(cls) -> int:
        return cls.upvotes - cls.downvotes

    @hybrid_property
    def vote_ratio(self):
        return self.upvotes / (self.upvotes + self.downvotes)

    @classmethod
    @vote_ratio.expression
    def vote_ratio(cls):
        return cls.upvotes / (cls.upvotes + cls.downvotes)

    @classmethod
    def add(
        cls,
        form: "CommentBodyType",
        thread: "Thread",
        user: "User",
        post: "Posts",
        comment: "Comments | None" = None,
    ):
        new_comment = Comments(
            user_id=user.id,
            content=form["content"],
            post_id=post.id,
        )
        if comment:
            comment.replies_count += 1
            new_comment.parent_id = comment.id
        if form["media"]:
            new_comment.media = Media.add(f"comments/{new_comment.id}", form=form)
        post.comment_count += 1
        user.comment_count += 1
        thread.comment_count += 1
        db.session.add(new_comment)
        return new_comment

    # noinspection DuplicatedCode
    def update(self, form: "CommentBodyType"):
        if form["media_id"] and self.media_id == form["media_id"].id:
            match form["operation"]:
                case OpType.UPDATE:
                    self.media.update(f"users/{self.username}", form=form)
                case OpType.DELETE:
                    self.media.delete()
        elif not form["media_id"] and form["operation"] == OpType.ADD and not self.media_id:
            self.media = Media.add(f"users/{self.username}", form=form)
        self.content = form["content"] or self.content
        # noinspection PyTypeChecker
        self.edited_at = datetime.now(tz=UTC)

    def delete(self, thread: "Thread", post: "Posts", user: "User", post_delete: bool = False):
        if not self.is_deleted:
            post.comment_count -= 1
            thread.comment_count -= 1
            user.comment_count -= 1
            if self.parent:
                self.parent.replies_count -= 1
            self.media.delete()
            # noinspection PyTypeChecker
            self.is_deleted = True
        if post_delete:
            for reaction in self.reaction:
                reaction.remove()
            db.session.delete(self)

    # noinspection PyTypeChecker
    def __init__(self, user_id: int, content: str, post_id: int):
        self.user_id = user_id
        self.post_id = post_id
        self.content = content
