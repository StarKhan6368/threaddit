from threaddit import db


class Subthread(db.Model):
    __tablename__ = "subthreads"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=db.func.now()
    )
    logo = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", back_populates="subthread")
    user_role = db.relationship("UserRole", back_populates="subthread")
    subscription = db.relationship("Subscription", back_populates="subthread")
    subthread_info = db.relationship("SubthreadInfo", back_populates="subthread")
    post = db.relationship("Posts", back_populates="subthread")
    post_info = db.relationship("PostInfo", back_populates="subthread")

    def as_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "logo": self.logo,
            "created_by": self.user.username,
            "subscriberCount": len(self.subscription),
            "modList": [
                r.user.username for r in self.user_role if r.role.slug == "moderator"
            ],
        }


class Subscription(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subthread_id = db.Column(db.Integer, db.ForeignKey("subthreads.id"), nullable=False)
    user = db.relationship("User", back_populates="subscription")
    subthread = db.relationship("Subthread", back_populates="subscription")


class SubthreadInfo(db.Model):
    __tablename__ = "subthread_info"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Integer, db.ForeignKey("subthreads.id"))
    logo = db.Column(db.Text)
    members_count = db.Column(db.Integer)
    posts_count = db.Column(db.Integer)
    comments_count = db.Column(db.Integer)
    subthread = db.relationship("Subthread", back_populates="subthread_info")

    def as_dict(self):
        return {
            "name": self.name,
            "logo": self.logo,
            "subscriberCount": self.members_count,
            "PostsCount": self.posts_count,
            "CommentsCount": self.comments_count,
        }
