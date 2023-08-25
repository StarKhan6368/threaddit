from threaddit import db
from flask_login import current_user
from threaddit.comments.models import Comments


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

    def as_dict(self, current_user_id=None):
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
                "media": self.media,
                "content": self.content,
                "created_at": self.created_at,
                "post_karma": self.post_karma,
                "comments_count": self.comments_count,
            },
        }
        if not current_user:
            return p_info
        else:
            has_reaction = Reactions.query.filter_by(
                post_id=self.post_id, user_id=current_user_id
            ).first()
            p_info["current_user"] = {
                "has_upvoted": has_reaction.is_upvote if has_reaction else False,
                "has_commented": bool(
                    Comments.query.filter_by(
                        post_id=self.post_id, user_id=current_user_id
                    ).first()
                ),
            }
        return p_info


class Reactions(db.Model):
    __tablename__ = "reactions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    is_upvote = db.Column(db.Boolean)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=db.func.now()
    )
    user = db.relationship("User", back_populates="reaction")
    comment = db.relationship("Comments", back_populates="reaction")
    post = db.relationship("Posts", back_populates="reaction")

    def as_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "post_id": self.post_id,
            "comment_id": self.comment_id,
            "is_upvote": self.is_upvote,
            "created_at": self.created_at,
        }
