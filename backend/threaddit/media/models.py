import enum
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import cloudinary.exceptions
from cloudinary import uploader
from flask import abort
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.utils import secure_filename

from threaddit import app, db

if TYPE_CHECKING:
    from threaddit.media.schemas import MediaFormType


class MediaType(enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    URL = "URL"


class Media(db.Model):
    __tablename__ = "media"
    id: Mapped[int] = mapped_column(primary_key=True)
    media_type: Mapped["MediaType"] = mapped_column(ENUM(MediaType, name="media_enum"), nullable=False)
    media_url: Mapped[str] = mapped_column(nullable=False)
    cldr_id: Mapped[str | None] = mapped_column(nullable=True, unique=True)
    created_on: Mapped[datetime] = mapped_column(nullable=False, default=db.func.now())

    # noinspection PyTypeChecker
    def __init__(self, media_type: "MediaType"):
        self.media_type = media_type

    @classmethod
    def add(cls, folder: str, form: "MediaFormType"):
        new_media = Media(media_type=form["media"]["type"])
        Media._parse_media(folder, form, new_media)
        db.session.add(new_media)
        return new_media

    @classmethod
    def _parse_media(cls, folder: str, form: "MediaFormType", media: "Media"):
        match form["media_type"]:
            case MediaType.URL:
                media.media_url = form["media"]["source"]
            case _:
                try:
                    media.cldr_id = Media._upload_media(folder, form)
                except cloudinary.exceptions.Error:
                    return abort(500, "Something went wrong with Cloudinary. Please try again later.")
                media.media_url = Media._cldr_to_url(form["media"]["type"], media.cldr_id)
        media.media_type = form["media"]["type"]
        return None

    def update(self, folder: str, form: "MediaFormType"):
        self._remove_media()
        Media._parse_media(folder, form, self)
        # noinspection PyTypeChecker
        self.created_on = datetime.now(tz=UTC)

    def delete(self):
        self._remove_media()
        db.session.delete(self)

    def _remove_media(self):
        if self.cldr_id:
            try:
                uploader.destroy(self.cldr_id)
            except cloudinary.exceptions.Error:
                return abort(500, "Something went wrong with Cloudinary. Please try again later.")
            print(f"Cloudinary Destroyed {self}")
        # noinspection PyTypeChecker
        self.cldr_id = None
        # noinspection PyTypeChecker
        self.media_url = None
        return None

    @classmethod
    def _upload_media(cls, folder: str, form: "MediaFormType") -> str:
        file_name = secure_filename(form["media"]["source"].filename).rsplit(".")[0]
        uploaded_media = uploader.upload(
            form["media"]["source"],
            resource_type=form["media_type"].name.lower(),
            public_id=f"{uuid.uuid4().hex}_{file_name}",
            folder=f"threaddit/{folder}",
        )
        print(f"Cloudinary Uploaded {uploaded_media}")
        return uploaded_media.get("public_id")

    @staticmethod
    def _cldr_to_url(media_type: "MediaType", cldr_id: str):
        match media_type:
            case MediaType.VIDEO:
                return (
                    f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}"
                    f"/video/upload/f_auto:video,q_auto:eco/{cldr_id}"
                )
            case MediaType.IMAGE:
                return (
                    f"https://res.cloudinary.com/{app.config['CLOUDINARY_NAME']}"
                    f"/image/upload/f_auto,q_auto:eco/{cldr_id}"
                )
            case MediaType.URL:
                return cldr_id

    def __repr__(self):
        return f"<Media {self.id} type={self.media_type} url={self.media_url}>"


class OpType(enum.Enum):
    ADD = "ADD"
    DELETE = "DELETE"
    UPDATE = "UPDATE"
    SKIP = "SKIP"
    NONE = "NONE"
