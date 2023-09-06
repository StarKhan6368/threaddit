from threaddit import db, ma, app
import os, uuid
from flask import jsonify, url_for
from datetime import datetime, timedelta
import cloudinary.uploader as uploader
from werkzeug.utils import secure_filename
from threaddit.subthreads.models import Subthread
from flask_marshmallow.fields import fields
from marshmallow.exceptions import ValidationError
from flask_login import current_user
from threaddit.comments.models import Comments
from threaddit.reactions.models import Reactions


class Posts(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    subthread_id = db.Column(db.Integer, db.ForeignKey("subthreads.id"))
    title = db.Column(db.Text, nullable=False)
    media = db.Column(db.Text)
    is_edited = db.Column(db.Boolean, default=False)
    content = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=db.func.now()
    )
    user = db.relationship("User", back_populates="post")
    subthread = db.relationship("Subthread", back_populates="post")
    post_info = db.relationship("PostInfo", back_populates="post")
    reaction = db.relationship("Reactions", back_populates="post")
    comment = db.relationship("Comments", back_populates="post")
    comment_info = db.relationship("CommentInfo", back_populates="post")
    saved_post = db.relationship("SavedPosts", back_populates="post")

    def get_media(self):
        if self.media and not self.media.startswith("http"):
            return url_for("send_image", filename=self.media)
        return self.media

    def patch(self, form_data, image):
        self.content = form_data.get("content", self.content)
        self.title = form_data.get("title", self.title)
        self.handle_media(
            form_data.get("content_type"), image, form_data.get("content_url")
        )
        self.is_edited = True
        db.session.commit()

    @classmethod
    def add(cls, form_data, image, user_id):
        new_post = Posts(
            user_id=user_id,
            subthread_id=form_data.get("subthread_id"),
            title=form_data.get("title"),
        )
        new_post.handle_media(
            form_data.get("content_type"), image, form_data.get("content_url")
        )
        if form_data.get("content"):
            new_post.content = form_data.get("content")
        db.session.add(new_post)
        db.session.commit()

    def handle_media(self, content_type, image=None, url=None):
        if content_type == "image" and image:
            self.delete_media()
            image_data = uploader.upload(
                image, public_id=f"{uuid.uuid4().hex}_{image.filename.rsplit('.')[0]}"
            )
            url = f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}/image/upload/f_auto,q_auto/{image_data.get('public_id')}"
            self.media = url
        elif content_type == "url" and url:
            self.media = url

    def __init__(self, user_id, subthread_id, title, media=None, content=None):
        self.user_id = user_id
        self.subthread_id = subthread_id
        self.title = title
        self.media = media
        self.content = content

    def delete_media(self):
        if self.media and self.media.startswith(
            f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}"
        ):
            res = uploader.destroy(self.media.split("/")[-1])
            print(f"Cloudinary Image Destory Response for {self.title}: ", res)

    def as_dict(self):
        return {
            "post_id": self.id,
            "is_edited": self.is_edited,
            "user_id": self.user_id,
            "subthread_id": self.subthread_id,
            "title": self.title,
            "media": self.get_media(),
            "content": self.content,
            "created_at": self.created_at,
        }


class SavedPosts(db.Model):
    __tablename__ = "saved"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=db.func.now()
    )
    user = db.relationship("User", back_populates="saved_post")
    post = db.relationship("Posts", back_populates="saved_post")

    def __init__(self, user_id, post_id):
        self.user_id = user_id
        self.post_id = post_id


class PostInfo(db.Model):
    __tablename__ = "post_info"
    thread_id = db.Column(db.Integer, db.ForeignKey("subthreads.id"))
    thread_name = db.Column(db.Text)
    thread_logo = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), primary_key=True)
    title = db.Column(db.Text)
    is_edited = db.Column(db.Boolean, default=False)
    media = db.Column(db.Text)
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user_name = db.Column(db.Text)
    user_avatar = db.Column(db.Text)
    post_karma = db.Column(db.Integer)
    comments_count = db.Column(db.Integer)
    post = db.relationship("Posts", back_populates="post_info")
    subthread = db.relationship("Subthread", back_populates="post_info")
    user = db.relationship("User", back_populates="post_info")

    def as_dict(self, cur_user=None):
        p_info = {
            "user_info": {
                "user_name": self.user_name,
                "user_avatar": self.user_avatar,
            },
            "thread_info": {
                "thread_id": self.thread_id,
                "thread_name": self.thread_name,
                "thread_logo": self.thread_logo,
            },
            "post_info": {
                "id": self.post_id,
                "title": self.title,
                "media": self.media,
                "is_edited": self.is_edited,
                "content": self.content,
                "created_at": self.created_at,
                "post_karma": self.post_karma,
                "comments_count": self.comments_count,
            },
        }
        if cur_user:
            has_reaction = Reactions.query.filter_by(
                post_id=self.post_id, user_id=cur_user
            ).first()
            p_info["current_user"] = {
                "has_upvoted": has_reaction.is_upvote if has_reaction else None,
            }
            p_info["post_info"] = p_info["post_info"] | {
                "saved": bool(
                    SavedPosts.query.filter_by(
                        user_id=cur_user, post_id=self.post_id
                    ).first()
                )
            }
        return p_info


def doesSubthreadExist(subthread_id):
    subthread = Subthread.query.filter_by(id=subthread_id).first()
    if not Subthread:
        raise ValidationError("Subthread does not exist")


class PostValidator(ma.SQLAlchemySchema):
    class Meta:
        model = Posts

    subthread_id = fields.Int(required=True, validate=[doesSubthreadExist])
    title = fields.Str(required=True)
    content = fields.Str(required=False)


def get_filters(sortby, duration):
    sortBy, durationBy = None, None
    match sortby:
        case "top":
            sortBy = PostInfo.post_karma.desc()
        case "new":
            sortBy = PostInfo.created_at.desc()
        case "hot":
            sortBy = PostInfo.comments_count.desc()
        case _:
            raise Exception("Invalid Sortby Request")
    match duration:
        case "day":
            durationBy = PostInfo.created_at.between(
                datetime.now() - timedelta(days=1), datetime.now()
            )
        case "week":
            durationBy = PostInfo.created_at.between(
                datetime.now() - timedelta(days=7), datetime.now()
            )
        case "month":
            durationBy = PostInfo.created_at.between(
                datetime.now() - timedelta(days=30), datetime.now()
            )
        case "year":
            durationBy = PostInfo.created_at.between(
                datetime.now() - timedelta(days=365), datetime.now()
            )
        case "alltime":
            durationBy = True
        case _:
            raise Exception("Invalid Duration Request")
    return sortBy, durationBy
