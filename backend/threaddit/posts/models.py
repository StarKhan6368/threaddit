import uuid
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import cloudinary.uploader as uploader
from marshmallow import Schema, fields, validate
from marshmallow.decorators import validates
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey
from werkzeug.utils import secure_filename

from threaddit import app, db
from threaddit.reactions.models import Reactions
from threaddit.subthreads.models import Subthread

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.users.models import User


class Posts(db.Model):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subthread_id: Mapped[int] = mapped_column(ForeignKey("subthreads.id"))
    title: Mapped[str] = mapped_column(nullable=False)
    media: Mapped[str | None] = mapped_column()
    is_edited: Mapped[bool] = mapped_column()
    content: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    karma_count: Mapped[int] = mapped_column(default=0)
    comment_count: Mapped[int] = mapped_column(default=0)
    user: Mapped["User"] = relationship(back_populates="post")
    subthread: Mapped["Subthread"] = relationship(back_populates="post")
    reaction: Mapped[list["Reactions"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    comment: Mapped[list["Comments"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    saved_post: Mapped[list["SavedPosts"]] = relationship(back_populates="post", cascade="all, delete-orphan")

    def patch(self, form_data, image):
        self.content = form_data.get("content", self.content)
        self.title = form_data.get("title", self.title)
        self.handle_media(form_data.get("content_type"), image, form_data.get("content_url"))
        self.is_edited = True
        db.session.commit()

    @classmethod
    def add(cls, form_data, image, user: "User", subthread: "Subthread"):
        new_post = Posts(
            user_id=user.id,
            subthread_id=form_data.get("subthread_id"),
            title=form_data.get("title"),
        )
        new_post.handle_media(form_data.get("content_type"), image, form_data.get("content_url"))
        if form_data.get("content"):
            new_post.content = form_data.get("content")
        subthread.post_count += 1
        user.post_count += 1
        db.session.add(new_post)
        db.session.commit()

    def remove(self):
        self.delete_media()
        self.subthread.post_count -= 1
        self.user.post_count -= 1
        for comment in self.comment:
            comment.remove()
        db.session.delete(self)
        db.session.commit()

    def handle_media(self, content_type, image=None, url=None):
        if content_type == "media" and image:
            self.delete_media()
            url = None
            filename = secure_filename(image.filename)
            if image.content_type.startswith("image/"):
                image_data = uploader.upload(
                    image,
                    public_id=f"{uuid.uuid4().hex}_{filename.rsplit('.')[0]}",
                )
                url = f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}/image/upload/c_auto,g_auto/{image_data.get('public_id')}"
            elif image.content_type.startswith("video/"):
                video_data = uploader.upload(
                    image,
                    resource_type="video",
                    public_id=f"{uuid.uuid4().hex}_{filename.rsplit('.')[0]}",
                )
                url = video_data.get("playback_url")
            self.media = url
        elif content_type == "url" and url:
            self.media = url

    def __init__(
        self, user_id: int, subthread_id: int, title: str, media: str | None = None, content: str | None = None
    ):
        self.user_id = user_id
        self.subthread_id = subthread_id
        self.title = title
        self.media = media
        self.content = content

    def delete_media(self):
        if self.media and self.media.startswith(f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}"):
            res = uploader.destroy(self.media.split("/")[-1])
            print(f"Cloudinary Image Destory Response for {self.title}: ", res)

    def as_dict(self, cur_user=None):
        p_info = {
            "user_info": {
                "user_name": self.user.username,
                "user_avatar": self.user.avatar,
            },
            "thread_info": {
                "thread_id": self.subthread.id,
                "thread_name": self.subthread.name,
                "thread_logo": self.subthread.logo,
            },
            "post_info": {
                "id": self.id,
                "title": self.title,
                "media": self.media,
                "is_edited": self.is_edited,
                "content": self.content,
                "created_at": self.created_at,
                "post_karma": self.karma_count,
                "comments_count": self.comment_count,
            },
        }
        if cur_user:
            has_reaction = Reactions.query.filter_by(post_id=self.id, user_id=cur_user).first()
            p_info["current_user"] = {
                "has_upvoted": has_reaction.is_upvote if has_reaction else None,
                "saved": bool(SavedPosts.query.filter_by(user_id=cur_user, post_id=self.id).first()),
            }
        return p_info


class SavedPosts(db.Model):
    __tablename__ = "saved"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    created_at: Mapped[datetime] = mapped_column(default=db.func.now())
    user: Mapped["User"] = relationship(back_populates="saved_post")
    post: Mapped["Posts"] = relationship(back_populates="saved_post")

    @classmethod
    def add(cls, user_id, post_id):
        new_saved = SavedPosts(user_id=user_id, post_id=post_id)
        db.session.add(new_saved)
        db.session.commit()
        return new_saved

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id


class PostSchema(Schema):
    subthread_id = fields.Int(required=True)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    content = fields.Str(required=False)

    @validates("title")
    def validate_title(self, title):
        if title.strip() == "":
            raise ValidationError("Title cannot be empty")

    @validates("subthread_id")
    def doesSubthreadExist(self, subthread_id):
        if not Subthread.query.filter_by(id=subthread_id).first():
            raise ValidationError("Subthread does not exist")


def get_filters(sortby, duration):
    sortBy, durationBy = None, None
    match sortby:
        case "top":
            sortBy = Posts.karma_count.desc()
        case "new":
            sortBy = Posts.created_at.desc()
        case "hot":
            sortBy = Posts.comment_count.desc()
        case _:
            raise Exception("Invalid Sortby Request")
    match duration:
        case "day":
            durationBy = Posts.created_at.between(datetime.now() - timedelta(days=1), datetime.now())
        case "week":
            durationBy = Posts.created_at.between(datetime.now() - timedelta(days=7), datetime.now())
        case "month":
            durationBy = Posts.created_at.between(datetime.now() - timedelta(days=30), datetime.now())
        case "year":
            durationBy = Posts.created_at.between(datetime.now() - timedelta(days=365), datetime.now())
        case "alltime":
            durationBy = False
        case _:
            raise Exception("Invalid Duration Request")
    return sortBy, durationBy
