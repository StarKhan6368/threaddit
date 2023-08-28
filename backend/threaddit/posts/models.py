from threaddit import db, ma, app
import base64
from flask import send_file
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

    def __init__(self, user_id, subthread_id, title, media=None, content=None):
        self.user_id = user_id
        self.subthread_id = subthread_id
        self.title = title
        self.media = media
        self.content = content

    def as_dict(self):
        return {
            "post_id": self.id,
            "user_id": self.user_id,
            "subthread_id": self.subthread_id,
            "title": self.title,
            "media": self.media,
            "content": self.content,
            "created_at": self.created_at,
        }


class PostInfo(db.Model):
    __tablename__ = "post_info"
    thread_id = db.Column(db.Integer, db.ForeignKey("subthreads.id"))
    thread_name = db.Column(db.Text)
    thread_logo = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), primary_key=True)
    title = db.Column(db.Text)
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

    def as_dict(self):
        if self.media and not str(self.media).startswith("http"):
            data = open(f"{app.config['UPLOAD_FOLDER']}/{self.media}", "rb").read()
            media = f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"
        else:
            media = self.media
        cur_user = current_user.id if current_user.is_authenticated else None
        p_info = {
            "user_info": {
                "user_name": self.user_name,
                "user_avatar": self.user_avatar,
            },
            "thread_info": {
                "thread_name": self.thread_name,
                "thread_logo": self.thread_logo,
            },
            "post_info": {
                "id": self.post_id,
                "title": self.title,
                "media": media,
                "content": self.content,
                "created_at": self.created_at,
                "post_karma": self.post_karma,
                "comments_count": self.comments_count,
            },
        }
        if not cur_user:
            return p_info
        else:
            has_reaction = Reactions.query.filter_by(
                post_id=self.post_id, user_id=cur_user
            ).first()
            p_info["current_user"] = {
                "has_upvoted": has_reaction.is_upvote if has_reaction else None,
                "has_commented": bool(
                    Comments.query.filter_by(
                        post_id=self.post_id, user_id=cur_user
                    ).first()
                ),
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
    title = fields.Str(required=True, validate=[fields.validate.Length(min=1, max=50)])
    content = fields.Str(required=False)
