from threaddit import db, app
from flask import url_for
from werkzeug.utils import secure_filename
import os
from threaddit.models import UserRole
import uuid


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

    @classmethod
    def add(cls, form_data, image, created_by):
        name = (
            form_data.get("name")
            if form_data.get("name").startswith("t/")
            else f"t/{form_data.get('name')}"
        )
        new_sub = Subthread(
            name=name,
            description=form_data.get("description"),
            created_by=created_by,
        )
        if form_data.get("content_type") == "image" and image:
            filename = secure_filename(image.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))
            new_sub.logo = unique_filename
        elif form_data.get("content_type") == "url":
            new_sub.logo = form_data.get("content_url")
        db.session.add(new_sub)
        db.session.commit()
        return new_sub

    def patch(self, form_data, image):
        self.handle_logo(
            form_data.get("content_type"), image, form_data.get("content_url")
        )
        if form_data.get("description"):
            self.description = form_data.get("description")
        db.session.commit()

    def handle_logo(self, content_type, image=None, url=None):
        if content_type == "image" and image:
            if self.logo and not self.logo.startswith("http"):
                os.remove(os.path.join(app.config["UPLOAD_FOLDER"], self.logo))
            filename = secure_filename(image.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_filename))
            self.logo = unique_filename
        elif content_type == "url" and url:
            self.logo = url

    def get_logo(self):
        if self.logo and not str(self.logo).startswith("http"):
            return url_for("send_image", filename=self.logo)
        return self.logo

    def as_dict(self, cur_user_id=None):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "logo": self.get_logo(),
            "PostsCount": len(self.post),
            "CommentsCount": self.comments_count or 0,
            "created_by": self.user.username,
            "subscriberCount": len(self.subscription),
            "modList": [
                r.user.username for r in self.user_role if r.role.slug == "mod"
            ],
        }
        if cur_user_id:
            data["has_subscribed"] = bool(
                Subscription.query.filter_by(
                    user_id=cur_user_id, subthread_id=self.id
                ).first()
            )
        return data

    def __init__(self, name, created_by, description=None, logo=None):
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

    @classmethod
    def add(cls, thread_id, user_id):
        new_sub = Subscription(user_id=user_id, subthread_id=thread_id)
        db.session.add(new_sub)
        db.session.commit()

    def __init__(self, user_id, subthread_id):
        self.user_id = user_id
        self.subthread_id = subthread_id


class SubthreadInfo(db.Model):
    __tablename__ = "subthread_info"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Integer, db.ForeignKey("subthreads.name"))
    logo = db.Column(db.Text)
    members_count = db.Column(db.Integer)
    posts_count = db.Column(db.Integer)
    comments_count = db.Column(db.Integer)
    subthread = db.relationship("Subthread", back_populates="subthread_info")

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "logo": self.subthread.get_logo(),
            "subscriberCount": self.members_count or 0,
            "PostsCount": self.posts_count or 0,
            "CommentsCount": self.comments_count or 0,
        }
