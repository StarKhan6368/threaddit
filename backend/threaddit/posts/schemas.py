import re
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, TypedDict

from marshmallow import ValidationError, fields, post_load, pre_dump, pre_load, validate
from sqlalchemy import UnaryExpression

from threaddit import ma
from threaddit.media.models import OpType
from threaddit.media.schemas import ImgVidSchema, MediaFormType, MediaSchema
from threaddit.posts.models import Posts
from threaddit.threads.schemas import ThreadLinkSchema
from threaddit.users.schemas import UserLinkSchema

if TYPE_CHECKING:
    from flask_sqlalchemy.pagination import Pagination


class PostFormType(TypedDict):
    title: str
    content: str
    media_list: list[MediaFormType]


class PostFeedType(TypedDict):
    limit: int
    page: int
    offset: int
    sort_by: UnaryExpression
    duration: UnaryExpression
    feed_name: str


class PostSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Posts
        exclude = ("user_id",)

    has_upvoted = fields.Bool(dump_default=False)  # :TODO: Fix this
    saved = fields.Bool(dump_default=False)  # :TODO: Fix this
    media = fields.Nested(MediaSchema(), data_key="media_list", many=True)
    karma = fields.Function(lambda post: post.upvotes - post.downvotes)
    user = fields.Nested(UserLinkSchema(), data_key="author")
    thread = fields.Nested(ThreadLinkSchema())


class PostResponseSchema(ma.Schema):
    posts = fields.Nested(PostSchema(), many=True)
    _meta = fields.Dict(keys=fields.String(), values=fields.Integer())

    # noinspection PyUnusedLocal
    @pre_dump
    def parse_data(self, data: "Pagination", **kwargs):  # noqa: ARG002
        return {
            "posts": data.items,
            "_meta": {"total": data.total, "pages": data.pages, "page": data.page, "limit": data.per_page},
        }


class PostFeedSchema(ma.Schema):
    limit = fields.Int(required=False, validate=validate.Range(min=1), load_default=10)
    page = fields.Int(required=False, validate=validate.Range(min=1), load_default=1)
    sort_by = fields.Str(
        required=False,
        validate=validate.OneOf(["top", "worst", "new", "old", "hot", "best", "controversial"]),
        load_default="top",
    )
    duration = fields.Str(
        required=False, validate=validate.OneOf(["alltime", "day", "week", "month", "year"]), load_default="alltime"
    )
    feed_name = fields.Str(required=False, validate=validate.OneOf(["home", "all", "popular"]), load_default="home")

    # noinspection PyUnusedLocal, DuplicatedCode
    @post_load
    def make_filters(self, data, **kwargs) -> "PostFeedSchema":  # noqa: ARG002
        match data["sort_by"]:
            case "top":
                # noinspection PyUnresolvedReferences
                data["sort_by"] = Posts.karma.desc()
            case "worst":
                # noinspection PyUnresolvedReferences
                data["sort_by"] = Posts.karma.asc()
            case "new":
                data["sort_by"] = Posts.created_at.desc()
            case "old":
                data["sort_by"] = Posts.created_at.asc()
            case "hot":
                data["sort_by"] = Posts.comment_count.desc()
            case "best":
                # noinspection PyUnresolvedReferences
                data["sort_by"] = Posts.vote_ratio.desc()
            case "controversial":
                # noinspection PyUnresolvedReferences
                data["sort_by"] = Posts.vote_ratio.asc()
            case _:
                raise ValidationError("Invalid Sort by Request", field_name="sort_by")

        match data["duration"]:
            case "day":
                data["duration"] = Posts.created_at.between(datetime.now(UTC) - timedelta(days=1), datetime.now(UTC))
            case "week":
                data["duration"] = Posts.created_at.between(datetime.now(UTC) - timedelta(days=7), datetime.now(UTC))
            case "month":
                data["duration"] = Posts.created_at.between(datetime.now(UTC) - timedelta(days=30), datetime.now(UTC))
            case "year":
                data["duration"] = Posts.created_at.between(datetime.now(UTC) - timedelta(days=365), datetime.now(UTC))
            case "alltime":
                data["duration"] = Posts.created_at.between(datetime(1970, 1, 1, tzinfo=UTC), datetime.now(UTC))
            case _:
                raise ValidationError("Invalid Duration Request", field_name="duration")

        data["offset"] = (data["page"] - 1) * data["limit"]
        return data


class PostFormSchema(ma.Schema):
    title = fields.Str(
        required=False,
        load_default=None,
        validate=[validate.Length(min=1, error="Title cannot be empty")],
    )
    content = fields.Str(required=False, validate=validate.Length(min=0, max=500), load_default=None)
    media_list = fields.List(fields.Nested(ImgVidSchema()), required=True)

    # noinspection PyUnusedLocal
    @post_load
    def check_indexes(self, data: "PostFormType", **kwargs):  # noqa: ARG002
        index_set = set()
        count = 0
        for form_media in data["media_list"]:
            if form_media["operation"] != OpType.DELETE:
                count += 1
                index_set.add(form_media["index"])

        unique_idx_set = set(range(1, count + 1))
        if index_set != unique_idx_set:
            raise ValidationError("Indexes Must be Unique & In-Sequence", field_name="media_list")
        return data

    # noinspection PyUnusedLocal
    @pre_load
    def make_media_list(self, data: "PostFormType", **kwargs):  # noqa: ARG002
        possible_count = sum(1 for key in data if "operation" in key)

        parsed = {}
        media_list = [{"media_type": None, "media": None} for _ in range(possible_count)]

        for key, value in data.items():
            if key in ("title", "content"):
                parsed[key] = value
                continue
            if res := re.match(r"^media_list\[(\d+)]\[(media_type|media|operation|media_id|index)]$", key):
                try:
                    media_list[int(res.group(1))] |= {res.group(2): value}
                except (IndexError, ValueError) as e:
                    raise ValidationError(
                        "Invalid Media Data, not enough operator fields", field_name="media_list"
                    ) from e
            else:
                raise ValidationError("Unknown field", field_name=key)

        return parsed | {"media_list": media_list}
