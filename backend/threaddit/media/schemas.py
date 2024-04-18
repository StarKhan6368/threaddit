import typing
from typing import Any, TypedDict

import urllib3
from flask_marshmallow import validate as ma_validate
from marshmallow import ValidationError, fields, pre_dump, validate, validates_schema
from werkzeug.datastructures import FileStorage

from threaddit import app, db, ma
from threaddit.media.models import Media, MediaType, OpType


class MediaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Media

    @pre_dump()
    def parse_fields(self, data: "Media", **_kwargs):
        data.media_type = data.media_type.value
        return data


class UrlOrFile(fields.Field):
    def __init__(self, img_only: bool = False, max_file_size: int = 10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_types = app.config["IMAGE_EXTENSIONS"]
        self.video_types = app.config["VIDEO_EXTENSIONS"]
        self.media_type = None
        self.max_file_size = max_file_size
        self.img_only = img_only
        if img_only:
            self.valid_ext = self.image_types
        else:
            self.valid_ext = self.image_types + self.video_types

    @property
    def media_type(self):
        return self._media_type

    @media_type.setter
    def media_type(self, value):
        if value == MediaType.VIDEO and not self.img_only:
            raise ValidationError("Invalid Media, must be an image", field_name="media")
        self._media_type = value

    def _validate_url(self, value, attr):
        if not any(value.endswith(ext) for ext in self.valid_ext):
            raise ValidationError("Invalid URL, Extension", field_name=attr)

        resp = urllib3.request("GET", value, retries=False)
        if resp.status != 200:  # noqa: PLR2004
            raise ValidationError("Invalid URL, Not Found", field_name=attr)

        content_type = resp.headers.get("content-type")

        if content_type.startswith("image"):
            self.media_type = MediaType.IMAGE
        elif content_type.startswith("video"):
            self.media_type = MediaType.VIDEO
        else:
            raise ValidationError("Invalid URL, Content Type", field_name=attr)

    def _validate_file(self, value: "FileStorage", attr):
        file_name = value.filename
        if any(file_name.endswith(ext) for ext in self.image_types):
            self.media_type = MediaType.IMAGE
        elif any(file_name.endswith(ext) for ext in self.video_types):
            self.media_type = MediaType.VIDEO
        else:
            raise ValidationError("Invalid File, Extension", field_name=attr)

    def _deserialize(
        self,
        value: str | None,
        attr: str | None,
        _data: typing.Mapping[str, Any] | None,
        **_kwargs,
    ) -> "_MediaType":
        if isinstance(value, str) and value.startswith("http"):
            validate.URL(schemes=["http", "https"], relative=False, error="Invalid URL")(value)
            self._validate_url(value, attr)

        elif isinstance(value, FileStorage):
            ma_validate.FileType(self.valid_ext)(value)
            ma_validate.FileSize(
                max=f"{self.max_file_size} MiB",
                error="File size should less than {max} MiB",
            )(value)
            self._validate_file(value, attr)
        else:
            raise ValidationError("Invalid URL or File", field_name=attr)

        return {"source": value, "type": self.media_type}


class TypeOfMedia(fields.Field):
    def __init__(self, image_only: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if image_only:
            self.valid_types = ("IMAGE", "URL")
        else:
            self.valid_types = ("IMAGE", "VIDEO", "URL")

    def _deserialize(
        self,
        value: str | None,
        _attr: str | None,
        _data: typing.Mapping[str, Any] | None,
        **_kwargs,
    ) -> "MediaType":
        validate.OneOf(self.valid_types)(value)
        return MediaType(value)


class OperationType(fields.Field):
    def _deserialize(
        self,
        value: str | None,
        _attr: str | None,
        _data: typing.Mapping[str, Any] | None,
        **_kwargs,
    ) -> OpType:
        validate.OneOf(OpType.__members__.keys())(value)
        return OpType(value)


class MediaId(fields.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _deserialize(
        self,
        value: int | None,
        attr: str | None,
        _data: typing.Mapping[str, Any] | None,
        **_kwargs,
    ) -> int | None:
        try:
            value = int(value)
        except (TypeError, ValueError) as e:
            raise ValidationError("Invalid Media ID", field_name=attr) from e

        if value and value < 0:
            raise ValidationError("Invalid Media ID", field_name=attr)

        media: "Media | None" = db.session.execute(db.select(Media).filter_by(id=value)).scalar_one_or_none()
        if not media:
            raise ValidationError("Invalid Media ID", field_name=attr)
        return media


class _MediaType(TypedDict):
    source: FileStorage | str
    type: MediaType


class MediaFormType(TypedDict):
    media_id: Media | None
    index: int
    operation: OpType
    media_type: MediaType | None
    media: _MediaType


def validate_media(data: "MediaFormType") -> "MediaFormType":
    match data["media_id"]:
        case None:
            if data["operation"] in (OpType.DELETE, OpType.UPDATE, OpType.SKIP):
                raise ValidationError("Media ID is required", field_name="media_id")
        case _:
            if data["operation"] == OpType.ADD:
                raise ValidationError("Media ID should be None for ADD", field_name="media_id")

    if data["operation"] == OpType.NONE:
        data["operation"] = OpType.DELETE

    media = data["media"]["source"] if data["media"] else None

    match data["media_type"]:
        case None:
            if data["media"]:
                raise ValidationError("Media Type is required", field_name="media_type")
        case MediaType.URL:
            if not media:
                raise ValidationError("Media is required", field_name="media")
            if not isinstance(media, str):
                raise ValidationError("Invalid URL", field_name="media")
        case _:
            if not media:
                raise ValidationError("Media is required", field_name="media")
            if not isinstance(media, FileStorage):
                raise ValidationError("Invalid File", field_name="media")

    return data


class ImageSchema(ma.Schema):
    media_id = MediaId(required=False, load_default=None)
    operation = OperationType(required=False, load_default=OpType.NONE)
    index = fields.Int(required=False, load_default=None)
    media_type = TypeOfMedia(image_only=True, load_default=None)
    media = UrlOrFile(img_only=True, max_file_size=10, load_default=None)

    @validates_schema
    def _validate_media(self, data, **_kwargs):
        validate_media(data)


class ImgVidSchema(ma.Schema):
    media_id = MediaId(required=False, load_default=None)
    operation = OperationType(required=False, load_default=OpType.NONE)
    index = fields.Int(required=False, load_default=None)
    media_type = TypeOfMedia(load_default=None)
    media = UrlOrFile(max_file_size=10, load_default=None)

    @validates_schema
    def _validate_media(self, data, **_kwargs):
        validate_media(data)
