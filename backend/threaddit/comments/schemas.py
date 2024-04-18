import re
from typing import TYPE_CHECKING, TypedDict

from flask_marshmallow import fields as ma_fields
from marshmallow import ValidationError, fields, post_dump, post_load, pre_dump, validate
from sqlalchemy import UnaryExpression

from threaddit import ma
from threaddit.comments.models import Comments
from threaddit.media.schemas import ImageSchema, MediaFormType, MediaSchema
from threaddit.users.schemas import UserLinkSchema

if TYPE_CHECKING:
    from flask_sqlalchemy.pagination import Pagination


class CommentBodyType(MediaFormType):
    content: str


class CommentsPaginateType(TypedDict):
    sort_by: UnaryExpression
    limit: int
    page: int
    offset: int


class CommentBodySchema(ImageSchema):
    content = fields.String(
        required=True,
        validate=[
            validate.Length(min=1, error="Comment cannot be empty"),
        ],
    )

    @post_load
    def validate_content(self, data, **_kwargs):
        if re.match(r"^\s*$", data["content"]):
            raise ValidationError("Comment cannot be empty", field_name="content")
        return data


class CommentsPaginateSchema(ma.Schema):
    sort_by = fields.Str(
        required=False,
        validate=validate.OneOf(["top", "worst", "new", "old", "hot", "best", "controversial"]),
        load_default="top",
    )
    page = fields.Integer(
        required=False, validate=validate.Range(min=1, error="Page cannot be less than 1"), load_default=1
    )
    limit = fields.Integer(
        required=False, validate=validate.Range(min=1, error="Limit cannot be less than 1"), load_default=20
    )

    # noinspection PyUnresolvedReferences, DuplicatedCode
    @post_load
    def make_filters(self, data: dict, **_kwargs) -> "CommentsPaginateType":
        match data["sort_by"]:
            case "top":
                data["sort_by"] = Comments.karma.desc()
            case "worst":
                data["sort_by"] = Comments.karma.asc()
            case "new":
                data["sort_by"] = Comments.created_at.desc()
            case "old":
                data["sort_by"] = Comments.created_at.asc()
            case "hot":  # :TODO: FIX
                data["sort_by"] = Comments.replies_count.desc()
            case "best":
                data["sort_by"] = Comments.vote_ratio.desc()
            case "controversial":
                data["sort_by"] = Comments.comment_count.asc()
            case _:
                raise ValidationError("Invalid Sort by Request", field_name="sort_by")

        data["offset"] = (data["page"] - 1) * data["limit"]

        return data


class CommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comments
        exclude = ("user_id", "post_id", "parent_id", "media_id")

    media = fields.Nested(MediaSchema(), data_key="media")
    user = fields.Nested(UserLinkSchema(), data_key="author")
    _links = ma_fields.Hyperlinks(
        {
            "replies": ma_fields.URLFor(
                "comments.comment_replies_get",
                values={"thread": "<post.thread_id>", "post": "<post_id>", "comment": "<id>"},
            ),
            "thread": ma_fields.URLFor(
                "threads.thread_get",
                values={"thread": "<post.thread_id>"},
            ),
            "post": ma_fields.URLFor("posts.post_get", values={"thread": "<post.thread_id>", "post": "<post_id>"}),
            "author": ma_fields.URLFor("users.user_get", values={"user": "<user.username>"}),
        }
    )

    # noinspection PyUnusedLocal
    @post_dump(pass_original=True)
    def check_deleted(self, data: dict, original: "Comments", **kwargs):  # noqa: ARG002
        if original.is_deleted:
            data["media"] = None
            data["content"] = "**deleted**"
            data["user"] = {"username": "**deleted**", "avatar": None}
        return data


class CommentsResponseSchema(ma.Schema):
    comments = fields.Nested(CommentSchema(), many=True)
    _meta = fields.Dict(keys=fields.String(), values=fields.Integer())

    # noinspection PyUnusedLocal
    @pre_dump
    def parse_data(self, data: "Pagination", **kwargs):  # noqa: ARG002
        return {
            "comments": data.items,
            "_meta": {"total": data.total, "pages": data.pages, "page": data.page, "limit": data.per_page},
        }
