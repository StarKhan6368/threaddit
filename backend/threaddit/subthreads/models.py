from threaddit import db, app
import base64


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

    def as_dict(self, cur_user_id=None):
        if self.logo and not str(self.logo).startswith("http"):
            data = open(f"{app.config['UPLOAD_FOLDER']}/{self.logo}", "rb").read()
            logo = f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"
        else:
            logo = self.logo
        return (
            {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "created_at": self.created_at,
                "logo": logo,
                "created_by": self.user.username,
                "subscriberCount": len(self.subscription),
                "modList": [
                    r.user.username for r in self.user_role if r.role.slug == "mod"
                ],
            }
            if not cur_user_id
            else {
                "has_subscribed": bool(
                    Subscription.query.filter_by(
                        user_id=cur_user_id, subthread_id=self.id
                    ).first()
                ),
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "created_at": self.created_at,
                "logo": logo,
                "created_by": self.user.username,
                "subscriberCount": len(self.subscription),
                "modList": [
                    r.user.username for r in self.user_role if r.role.slug == "mod"
                ],
            }
        )

    def __init__(self, name, description, logo, created_by):
        self.name = name
        self.description = description
        self.logo = logo
        self.created_by = created_by


class Subscription(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subthread_id = db.Column(db.Integer, db.ForeignKey("subthreads.id"), nullable=False)
    user = db.relationship("User", back_populates="subscription")
    subthread = db.relationship("Subthread", back_populates="subscription")

    def __init__(self, user_id, subthread_id):
        self.user_id = user_id
        self.subthread_id = subthread_id


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
        if self.logo and not str(self.logo).startswith("http"):
            data = open(f"{app.config['UPLOAD_FOLDER']}/{self.logo}", "rb").read()
            logo = f"data:image/jpeg;base64,{base64.b64encode(data).decode('utf-8')}"
        else:
            logo = self.logo
        return {
            "id": self.id,
            "name": self.name,
            "logo": logo,
            "subscriberCount": self.members_count or 0,
            "PostsCount": self.posts_count or 0,
            "CommentsCount": self.comments_count or 0,
        }
