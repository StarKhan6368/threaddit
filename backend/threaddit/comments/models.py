from threaddit import db
from threaddit.reactions.models import Reactions


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    is_edited = db.Column(db.Boolean, default=False)
    has_parent = db.Column(db.Boolean)
    content = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=db.func.now()
    )
    reaction = db.relationship("Reactions", back_populates="comment")
    user = db.relationship("User", back_populates="comment")
    post = db.relationship("Posts", back_populates="comment")
    comment_info = db.relationship("CommentInfo", back_populates="comment")

    @classmethod
    def add(cls, form_data, user_id):
        new_comment = Comments(
            user_id=user_id,
            content=form_data["content"],
            post_id=form_data["post_id"],
        )
        if form_data.get("has_parent", False):
            new_comment.has_parent = True
            new_comment.parent_id = form_data["parent_id"]
        db.session.add(new_comment)
        db.session.commit()
        return new_comment.comment_info[0].as_dict(user_id)

    def patch(self, content):
        if content:
            self.content = content
            self.is_edited = True
            db.session.commit()

    def __init__(self, user_id, content, post_id=None, has_parent=None, parent_id=None):
        self.user_id = user_id
        self.post_id = post_id
        self.content = content
        self.has_parent = has_parent
        self.parent_id = parent_id


class CommentInfo(db.Model):
    __tablename__ = "comment_info"
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"), primary_key=True)
    user_name = db.Column(db.Text)
    user_avatar = db.Column(db.Text)
    comment_karma = db.Column(db.Integer)
    has_parent = db.Column(db.Boolean)
    parent_id = db.Column(db.Integer)
    content = db.Column(db.Text)
    is_edited = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(timezone=True))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    post = db.relationship("Posts", back_populates="comment_info")
    comment = db.relationship("Comments", back_populates="comment_info")

    def as_dict(self, cur_user):
        comment_info = {
            "user_info": {
                "user_name": self.user_name,
                "user_avatar": self.user_avatar,
            },
            "comment_info": {
                "id": self.comment_id,
                "content": self.content,
                "created_at": self.created_at,
                "comment_karma": self.comment_karma,
                "has_parent": self.has_parent,
                "is_edited": self.is_edited,
                "parent_id": self.parent_id,
            },
        }
        if cur_user:
            has_reaction = Reactions.query.filter_by(
                comment_id=self.comment_id, user_id=cur_user
            ).first()
            comment_info["current_user"] = {
                "has_upvoted": has_reaction.is_upvote if has_reaction else None
            }
        return comment_info
