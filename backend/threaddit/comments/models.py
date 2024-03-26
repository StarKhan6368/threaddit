from datetime import datetime
from typing import TYPE_CHECKING

from marshmallow import Schema, fields, validate
from marshmallow.decorators import validates
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

from threaddit import db
from threaddit.posts.models import Posts
from threaddit.reactions.models import Reactions

if TYPE_CHECKING:
    from threaddit.users.models import User


class Comments(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    is_edited: Mapped[bool] = mapped_column()
    has_parent: Mapped[bool | None] = mapped_column()
    content: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=db.func.now(), nullable=False)
    karma_count: Mapped[int] = mapped_column(default=0)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    reaction: Mapped[list["Reactions"]] = relationship(back_populates="comment", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship(back_populates="comment")
    post: Mapped["Posts"] = relationship(back_populates="comment")
    parent: Mapped["Comments"] = relationship(back_populates="children", remote_side="Comments.id")
    children: Mapped[list["Comments"]] = relationship(
        back_populates="parent", cascade="all, delete-orphan", foreign_keys="Comments.parent_id"
    )

    @classmethod
    def add(cls, form_data, cur_user: int, post: "Posts"):
        new_comment = Comments(
            user_id=cur_user,
            content=form_data["content"],
            post_id=form_data["post_id"],
        )
        if form_data.get("has_parent", False):
            new_comment.has_parent = True
            new_comment.parent_id = form_data["parent_id"]
        post.comment_count += 1
        post.user.comment_count += 1
        post.subthread.comment_count += 1
        db.session.add(new_comment)
        db.session.commit()
        return new_comment.as_dict()

    def patch(self, content):
        if content:
            self.content = content
            self.is_edited = True
            db.session.commit()

    def remove(self, post_delte: bool = False):
        if not self.is_deleted:
            self.post.comment_count -= 1
            self.post.user.comment_count -= 1
            self.post.subthread.comment_count -= 1
        if post_delte:
            for reaction in self.reaction:
                reaction.remove()
            db.session.delete(self)
        else:
            self.is_deleted = True
        db.session.commit()

    def __init__(
        self, user_id: int, content: str, post_id: int, has_parent: bool | None = None, parent_id: int | None = None
    ):
        self.user_id = user_id
        self.post_id = post_id
        self.content = content
        self.has_parent = has_parent
        self.parent_id = parent_id

    def as_dict(self, cur_user: int | None = None):
        comment_info = {
            "user_info": {
                "user_name": self.user.username,
                "user_avatar": self.user.avatar,
            },
            "comment_info": {
                "id": self.id,
                "content": self.content if not self.is_deleted else "**[deleted]**",
                "is_deleted": self.is_deleted,
                "created_at": self.created_at,
                "comment_karma": self.karma_count,
                "has_parent": self.has_parent,
                "is_edited": self.is_edited,
                "parent_id": self.parent_id,
            },
        }
        if cur_user:
            has_reaction = Reactions.query.filter_by(comment_id=self.id, user_id=cur_user).first()
            comment_info["current_user"] = {"has_upvoted": has_reaction.is_upvote if has_reaction else None}
        return comment_info


class CommentSchema(Schema):
    content = fields.Str(required=True, validate=validate.Length(min=1))
    post_id = fields.Int(required=True)
    has_parent = fields.Bool()
    parent_id = fields.Int()

    @validates("content")
    def validate_content(self, content):
        if content.strip() == "":
            raise ValidationError("Comment cannot be empty")

    @validates("post_id")
    def doesPostExist(self, post_id):
        if not Posts.query.filter_by(id=post_id).first():
            raise ValidationError("Post does not exist")

    @validates("parent_id")
    def doesCommentExist(self, parent_id):
        if parent_id and not Comments.query.filter_by(id=parent_id).first():
            raise ValidationError("Parent Comment does not exist")
