import uuid
from datetime import datetime

import cloudinary.uploader as uploader
from flask_login import UserMixin
from marshmallow import Schema, fields, validate
from marshmallow.decorators import validates
from marshmallow.exceptions import ValidationError
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing_extensions import TYPE_CHECKING

from threaddit import app, db, login_manager

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.messages.models import Messages
    from threaddit.models import UserRole
    from threaddit.posts.models import Posts, SavedPosts
    from threaddit.reactions.models import Reactions
    from threaddit.subthreads.models import Subscription, Subthread


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__: str = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    avatar: Mapped[str] = mapped_column()
    bio: Mapped[str] = mapped_column()
    post_karma: Mapped[int] = mapped_column(default=0, nullable=False)
    comment_karma: Mapped[int] = mapped_column(default=0, nullable=False)
    post_count: Mapped[int] = mapped_column(default=0, nullable=False)
    comment_count: Mapped[int] = mapped_column(default=0, nullable=False)
    registration_date: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())
    subthread: Mapped[list["Subthread"]] = relationship(back_populates="user")
    user_role: Mapped[list["UserRole"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscription: Mapped[list["Subscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    post: Mapped[list["Posts"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    comment: Mapped[list["Comments"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    reaction: Mapped[list["Reactions"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    saved_post: Mapped[list["SavedPosts"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sender: Mapped[list["Messages"]] = relationship(
        back_populates="user_sender", foreign_keys="Messages.sender_id", cascade="all, delete-orphan"
    )
    receiver: Mapped[list["Messages"]] = relationship(
        back_populates="user_receiver",
        foreign_keys="Messages.receiver_id",
        cascade="all, delete-orphan",
    )

    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def get_id(self):
        return str(self.id)

    def add(self):
        db.session.add(self)
        db.session.commit()

    def patch(self, image, form_data: dict):
        if form_data.get("content_type") == "image" and image:
            self.delete_avatar()
            image_data = uploader.upload(image, public_id=f"{uuid.uuid4().hex}_{image.filename.rsplit('.')[0]}")
            url = f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}/image/upload/f_auto,q_auto/{image_data.get('public_id')}"
            self.avatar = url
        elif form_data.get("content_type") == "url":
            self.avatar = form_data.get("content_url", self.avatar)
        self.bio = form_data.get("bio", self.bio)
        db.session.commit()

    def delete_avatar(self):
        if self.avatar and self.avatar.startswith(f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}"):
            res = uploader.destroy(self.avatar.split("/")[-1])
            print(f"Cloudinary Image Destory Response for {self.username}: ", res)

    def has_role(self, role: int):
        return role in {r.role.slug for r in self.user_role}

    @classmethod
    def get_all(cls):
        all_users: list[dict] = []
        for user in cls.query.all():
            all_users.append(user.as_dict(include_all=True))
        return all_users

    def as_dict(self, include_all=False) -> dict:
        data = {
            "username": self.username,
            "avatar": self.avatar,
            "bio": self.bio,
            "registrationDate": self.registration_date,
            "roles": list({r.role.slug for r in self.user_role}),
            "karma": {
                "comments_count": self.comment_count,
                "comments_karma": self.comment_karma,
                "posts_count": self.post_count,
                "posts_karma": self.post_karma,
                "user_karma": self.post_karma + self.comment_karma,
            },
            "mod_in": [r.subthread_id for r in self.user_role if r.role.slug == "mod"],
        }
        if not include_all:
            return data
        else:
            return {"id": self.id, "email": self.email, **self.as_dict()}


class LoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

    @validates("email")
    def valid_email(self, value):
        if not User.query.filter_by(email=value).first():
            raise ValidationError("Email does not exist")


class RegisterSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))

    @validates("email")
    def valid_email(self, value):
        if User.query.filter_by(email=value).first():
            raise ValidationError("Email already exists")

    @validates("username")
    def valid_username(self, value):
        if User.query.filter_by(username=value).first():
            raise ValidationError("Username already exists")
