from sqlalchemy import func
from flask import url_for
import cloudinary.uploader as uploader
import uuid, cloudinary
from threaddit import db, login_manager, app
from flask_login import UserMixin
from threaddit import ma, app
from threaddit.models import Role, UserRole
from werkzeug.utils import secure_filename
from flask_marshmallow.fields import fields
from marshmallow.exceptions import ValidationError


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class User(db.Model, UserMixin):
    __tablename__: str = "users"
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.Text, unique=True, nullable=False)
    email: str = db.Column(db.Text, unique=True, nullable=False)
    password_hash: str = db.Column(db.Text, nullable=False)
    avatar: str = db.Column(db.Text)
    bio: str = db.Column(db.Text)
    registration_date = db.Column(
        db.DateTime(timezone=True), nullable=False, default=db.func.now()
    )
    subthread = db.relationship("Subthread", back_populates="user")
    user_role = db.relationship("UserRole", back_populates="user")
    subscription = db.relationship("Subscription", back_populates="user")
    user_karma = db.relationship("UsersKarma", back_populates="user")
    post = db.relationship("Posts", back_populates="user")
    post_info = db.relationship("PostInfo", back_populates="user")
    comment = db.relationship("Comments", back_populates="user")
    reaction = db.relationship("Reactions", back_populates="user")
    saved_post = db.relationship("SavedPosts", back_populates="user")
    sender = db.relationship(
        "Messages", back_populates="user_sender", foreign_keys="Messages.sender_id"
    )
    receiver = db.relationship(
        "Messages", back_populates="user_receiver", foreign_keys="Messages.receiver_id"
    )

    def __init__(self, username: str, email: str, password_hash: str):
        self.username = username
        self.email = email
        self.password_hash = password_hash

    def get_id(self):
        return self.id

    def add(self):
        db.session.add(self)
        db.session.commit()

    def patch(self, image, form_data):
        if form_data.get("content_type") == "image" and image:
            self.delete_avatar()
            image_data = uploader.upload(
                image, public_id=f"{uuid.uuid4().hex}_{image.filename.rsplit('.')[0]}"
            )
            url = f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}/image/upload/f_auto,q_auto/{image_data.get('public_id')}"
            self.avatar = url
        elif form_data.get("content_type") == "url":
            self.avatar = form_data.get("content_url")
        self.bio = form_data.get("bio")
        db.session.commit()

    def delete_avatar(self):
        if self.avatar and self.avatar.startswith(
            f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}"
        ):
            res = uploader.destroy(self.avatar.split("/")[-1])
            print(f"Cloudinary Image Destory Response for {self.username}: ", res)

    def has_role(self, role):
        return role in {r.role.slug for r in self.user_role}

    @classmethod
    def get_all(cls):
        all_users: list[dict] = []
        for user in cls.query.all():
            all_users.append(user.as_dict(include_all=True))
        return all_users

    def as_dict(self, include_all=False) -> dict:
        return (
            {
                "username": self.username,
                "avatar": self.avatar,
                "bio": self.bio,
                "registrationDate": self.registration_date,
                "roles": list({r.role.slug for r in self.user_role}),
                "karma": self.user_karma[0].as_dict(),
                "mod_in": [
                    r.subthread_id for r in self.user_role if r.role.slug == "mod"
                ],
            }
            if not include_all
            else {"id": self.id, "email": self.email, **self.as_dict()}
        )


def username_validator(username: str):
    if (
        db.session.query(User)
        .filter(func.lower(User.username) == username.lower())
        .first()
    ):
        raise ValidationError("Username already exists")


def email_validator(email: str):
    if User.query.filter_by(email=email).first():
        raise ValidationError("Email already exists")


class UserLoginValidator(ma.SQLAlchemySchema):
    class Meta:
        model = User

    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=[fields.validate.Length(min=8)])


class UserRegisterValidator(ma.SQLAlchemySchema):
    class Meta:
        model = User

    username = fields.Str(
        required=True,
        validate=[
            fields.validate.Length(
                min=4, max=15, error="Username must be between 1 and 50 characters"
            ),
            fields.validate.Regexp(
                "^[a-zA-Z][a-zA-Z0-9_]*$",
                error="Username must start with a letter, and contain only \
                letters, numbers, and underscores.",
            ),
            username_validator,
        ],
    )
    email = fields.Email(required=True, validate=[email_validator])
    password = fields.Str(required=True, validate=[fields.validate.Length(min=8)])


class UsersKarma(db.Model):
    __tablename__: str = "user_info"
    user_id: int = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False, primary_key=True
    )
    user_karma: int = db.Column(db.Integer, nullable=False)
    comments_count: int = db.Column(db.Integer, nullable=False)
    comments_karma: int = db.Column(db.Integer, nullable=False)
    posts_count: int = db.Column(db.Integer, nullable=False)
    posts_karma: int = db.Column(db.Integer, nullable=False)
    user = db.relationship("User", back_populates="user_karma")

    def as_dict(self) -> dict:
        return {
            "user_karma": self.user_karma,
            "comments_count": self.comments_count,
            "comments_karma": self.comments_karma,
            "posts_count": self.posts_count,
            "posts_karma": self.posts_karma,
        }
