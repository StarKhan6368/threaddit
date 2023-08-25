from threaddit import db


class Comments(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    parent_id = db.Column(db.Integer, db.ForeignKey("comments.id"))
    is_parent = db.Column(db.Boolean)
    content = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=db.func.now()
    )
    reaction = db.relationship("Reactions", back_populates="comment")
    user = db.relationship("User", back_populates="comment")
    post = db.relationship("Posts", back_populates="comment")
