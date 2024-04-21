import re
from typing import TYPE_CHECKING, TypedDict

from flask_jwt_extended import current_user
from flask_marshmallow import fields as ma_fields
from marshmallow import ValidationError, fields, post_dump, post_load, pre_dump, pre_load, validate

from threaddit import ma
from threaddit.media.schemas import ImageSchema, MediaFormType, MediaSchema
from threaddit.threads.models import Thread
from threaddit.users.schemas import UserLinkSchema

if TYPE_CHECKING:
    from flask_sqlalchemy.pagination import Pagination


class ThreadFormType(TypedDict):
    name: str
    description: str | None
    logo: MediaFormType | None
    banner: MediaFormType | None
    rules: str | None
    join_message: str | None


class PaginationType(TypedDict):
    limit: int
    page: int


class FlairsType(TypedDict):
    flairs: list[str]


class ThreadFlairsSchema(ma.Schema):
    flairs = fields.List(fields.String(required=True, validate=validate.Length(min=3, max=15)), required=True)

    # noinspection PyUnusedLocal
    @post_load
    def check_flair(self, data: "FlairsType", **kwargs) -> "FlairsType":  # noqa: ARG002
        for flair in data["flairs"]:
            if re.match(r"^\s*$", flair):
                error = f"Flair {flair} cannot be empty spaces"
                raise ValidationError(error, field_name="flairs")
        return data


class ThreadFormSchema(ma.Schema):
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, error="Thread Name must be at least 3 characters long"),
            validate.Regexp(
                "^[a-zA-Z0-9_-]+$",
                error="Thread Name must only contain letters, numbers, dashes and underscores",
            ),
        ],
    )
    description = fields.String(required=False, validate=validate.Length(min=0, max=1000), load_default=None)
    rules = fields.String(required=False, validate=validate.Length(min=0, max=1000), load_default=None)
    join_message = fields.String(required=False, validate=validate.Length(min=0, max=1000), load_default=None)
    logo = fields.Nested(ImageSchema(), required=False, load_default=None)
    banner = fields.Nested(ImageSchema(), required=False, load_default=None)

    @pre_load
    def validate_description(self, data: dict, **_kwargs):
        parsed_data = {"banner": {}, "logo": {}}

        for key, val in data.items():
            if match := re.match(r"^(banner|logo)\[(media|media_id|operation|media_type)]", key):
                parsed_data[match.group(1)] |= {match.group(2): val}
            elif key in ("description", "rules", "join_message"):
                parsed_data[key] = val
            else:
                raise ValidationError("Unknown field", field_name=key)

        if parsed_data.get("description") and re.match(r"^\s*$", parsed_data["description"]):
            raise ValidationError("Description cannot be empty spaces", field_name="description")

        return parsed_data


class PaginationSchema(ma.Schema):
    limit = fields.Int(required=False, validate=validate.Range(min=1), load_default=10)
    page = fields.Int(required=False, validate=validate.Range(min=1), load_default=1)


class ThreadLinkSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Thread
        fields = ("name", "id", "media", "is_subscribed", "subscriber_count", "logo")

    is_subscribed = fields.Bool()
    logo = fields.Nested(MediaSchema())


class ThreadBarSchema(ma.Schema):
    threads = fields.Nested(ThreadLinkSchema(), many=True)
    _meta = fields.Dict(keys=fields.String(), values=fields.Integer())

    @pre_dump
    def parse_threads(self, data: "Pagination", **_kwargs):
        return {
            "threads": data.items,
            "_meta": {"total": data.total, "pages": data.pages, "page": data.page, "limit": data.per_page},
        }


class ThreadSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Thread
        exclude = ("join_message",)

    is_subscribed = fields.Bool()
    logo = fields.Nested(MediaSchema())
    banner = fields.Nested(MediaSchema())
    flairs = fields.List(fields.String())
    creator = fields.Nested(UserLinkSchema(), data_key="creator")

    _links = ma_fields.Hyperlinks(
        {
            "self": ma_fields.URLFor("threads.thread_get", values={"thread": "<id>"}),
            "posts": ma_fields.URLFor("posts.thread_posts", values={"thread": "<id>"}),
            "comments": ma_fields.URLFor("comments.thread_comments_get", values={"thread": "<id>"}),
            "moderators": ma_fields.URLFor("moderation.thread_moderators_get", values={"thread": "<id>"}),
            "report_types": ma_fields.URLFor("reports.thread_report_types_get", values={"thread": "<id>"}),
        }
    )

    # noinspection PyUnusedLocal
    @post_dump(pass_original=True)
    def add_fields(self, data: dict, thread: "Thread", **kwargs):  # noqa: ARG002
        if current_user.is_admin or current_user.moderator_in(thread):
            data["join_message"] = thread.join_message

        return data
