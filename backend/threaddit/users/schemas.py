import re
from typing import TypedDict

from flask_jwt_extended import current_user
from flask_marshmallow import fields as ma_fields
from marshmallow import ValidationError, fields, post_dump, post_load, validate

from threaddit import ma
from threaddit.media.schemas import ImageSchema, MediaFormType, MediaSchema
from threaddit.users.models import User


class LoginType(TypedDict):
    email: str
    password: str


class RegisterType(TypedDict):
    email: str
    user_name: str
    password: str


class UserFormType(MediaFormType):
    bio: str | None


class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=8))


class RegisterSchema(ma.Schema):
    email = fields.Email(required=True, error_messages={"required": "Email cannot be empty"})
    user_name = fields.String(
        required=True,
        validate=[
            validate.Regexp(r"^[a-zA-Z0-9_\s]+$", error=f"Invalid User Name {input}"),
            validate.Length(min=4, error="User Name must be at least 4 characters long"),
        ],
        error_messages={"required": "User Name cannot be empty"},
    )
    password = fields.String(
        required=True, validate=validate.Length(min=8), error_messages={"required": "Password cannot be empty"}
    )


class UserFormSchema(ImageSchema):
    bio = fields.String(required=False, validate=[validate.Length(min=0, max=100)], load_default=None)

    @post_load
    def validate_bio(self, data, **_kwargs):
        if data["bio"] and re.match(r"^\s*$", data["bio"]):
            raise ValidationError("Bio cannot be empty spaces", field_name="bio")
        return data


class UserLinkSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("username", "media")

    media = fields.Nested(MediaSchema(), data_key="avatar")
    _links = ma_fields.Hyperlinks(
        {
            "self": ma_fields.URLFor("users.user_get", values={"user": "<username>"}),
        },
    )


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ("id", "password_hash", "email")

    media = fields.Nested(MediaSchema(), data_key="avatar")
    _links = ma_fields.Hyperlinks(
        {
            "self": ma_fields.URLFor("users.user_get", values={"user": "<username>"}),
            "posts": ma_fields.URLFor("posts.user_posts_get", values={"user": "<username>"}),
            "comments": ma_fields.URLFor("comments.user_comments_get", values={"user": "<username>"}),
            "saved_posts": ma_fields.URLFor("posts.user_saved_posts_get"),
            "saved_comments": ma_fields.URLFor("comments.user_saved_comments_get"),
        },
    )

    # noinspection PyUnusedLocal
    @post_dump(pass_original=True)
    def saved_res(self, data: dict, user: "User", **kwargs):  # noqa: ARG002
        if current_user:
            data["email"] = user.email
        return data
