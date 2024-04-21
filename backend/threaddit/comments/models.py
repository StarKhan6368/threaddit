from datetime import UTC, datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import abort
from flask_jwt_extended import current_user
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db
from threaddit.media.models import Media, OpType
from threaddit.notifications.models import Notifications, NotifType
from threaddit.reactions.models import Reactions
from threaddit.saves.models import Saves

if TYPE_CHECKING:
    from threaddit.comments.schemas import CommentBodyType
    from threaddit.posts.models import Posts
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
    depth: Mapped[int] = mapped_column(nullable=False, default=0)
    saved_count: Mapped[int] = mapped_column(default=0)
    report_count: Mapped[int] = mapped_column(default=0)
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_removed: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_locked: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_sticky: Mapped[bool] = mapped_column(default=False, nullable=False)
    replies_count: Mapped[int] = mapped_column(default=0, nullable=False)
    disable_reports: Mapped[bool] = mapped_column(default=False, nullable=False)
    reaction: Mapped[list["Reactions"]] = relationship(back_populates="comment")
    media: Mapped["Media"] = relationship()
    user: Mapped["User"] = relationship(back_populates="comments")
    post: Mapped["Posts"] = relationship(back_populates="comment")
    parent: Mapped["Comments"] = relationship(back_populates="children", remote_side="Comments.id")
    children: Mapped[list["Comments"]] = relationship(back_populates="parent", foreign_keys="Comments.parent_id")

    @property
    def has_upvoted(self):
        reaction = db.session.scalar(
            sa.select(Reactions).where(Reactions.user_id == current_user.id, Reactions.comment_id == self.id)
        )
        return reaction.is_upvote if reaction else None

    @property
    def has_saved(self):
        saved_comment = db.session.scalar(
            sa.select(Saves).where(Saves.user_id == current_user.id, Saves.comment_id == self.id)
        )
        return saved_comment is not None

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

    @staticmethod
    def add(
        form: "CommentBodyType",
        thread: "Thread",
        user: "User",
        post: "Posts",
        comment: "Comments|None" = None,
    ):
        new_comment = Comments(
            user_id=user.id,
            content=form["content"],
            post_id=post.id,
        )
        if comment:
            comment.replies_count += 1
            new_comment.parent_id = comment.id
            new_comment.depth = comment.depth + 1
        if form["media"]:
            new_comment.media = Media.add(f"comments/{new_comment.id}", form=form)
        post.comment_count += 1
        user.comment_count += 1
        thread.comment_count += 1
        db.session.add(new_comment)
        new_comment.notify_user(user, thread, post, comment)
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
            if self.media:
                self.media.delete()
            # noinspection PyTypeChecker
            self.is_deleted = True
        if post_delete:
            for reaction in self.reaction:
                reaction.remove()
            db.session.delete(self)

    def notify_user(
        self,
        user: "User",
        thread: "Thread",
        post: "Posts",
        comment: "Comments|None" = None,
    ):
        if comment and comment.user_id == user.id or post.user_id == user.id:
            return
        if comment:
            Notifications.notify(
                NotifType.COMMENT_REPLY,
                user=comment.user,
                title=f"{user.username} replied to your comment on {thread.name}",
                sub_title=comment.content,
                content=self.content,
                res_id=post.id,
                res_media_id=user.avatar_id,
            )
        else:
            Notifications.notify(
                NotifType.POST_COMMENT,
                user=post.user,
                title=f"{user.username} commented on your post on {thread.name}",
                sub_title=post.title,
                content=self.content,
                res_id=post.id,
                res_media_id=user.avatar_id,
            )

    def validate_comment(self, thread: "Thread", post: "Posts"):
        post.validate_post(thread)
        if self.post_id != post.id:
            return abort(400, {"message": f"Comment does not belong to post {post.id}"})
        return None

    # noinspection PyTypeChecker
    def __init__(self, user_id: int, content: str, post_id: int):
        self.user_id = user_id
        self.post_id = post_id
        self.content = content
