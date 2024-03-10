from threaddit import db


class Reactions(db.Model):
    __tablename__ = "reactions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    comment_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    is_upvote = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=db.func.now())
    user = db.relationship("User", back_populates="reaction")
    comment = db.relationship("Comments", back_populates="reaction")
    post = db.relationship("Posts", back_populates="reaction")

    def __init__(self, user_id, is_upvote, post_id=None, comment_id=None):
        self.user_id = user_id
        self.post_id = post_id
        self.comment_id = comment_id
        self.is_upvote = is_upvote

    @classmethod
    def add(cls, user_id, is_upvote, post_id=None, comment_id=None):
        new_reaction = Reactions(user_id=user_id, is_upvote=is_upvote, post_id=post_id, comment_id=comment_id)
        db.session.add(new_reaction)
        db.session.commit()

    def patch(self, is_upvote):
        self.is_upvote = is_upvote
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
