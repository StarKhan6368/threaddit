import re

from flask_jwt_extended import current_user
from marshmallow import ValidationError, fields, post_load, validate

from threaddit import ma
from threaddit.media.schemas import ImgVidSchema, MediaFormType
from threaddit.messages.models import Messages
from threaddit.users.schemas import UserLinkSchema


class MessageFormType(MediaFormType):
    content: str


class MessageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Messages
        exclude = ("sender_id", "receiver_id")

    user_sender = fields.Nested(UserLinkSchema(), data_key="sender")
    user_receiver = fields.Nested(UserLinkSchema(), data_key="receiver")
    user_relation = fields.String(validate=validate.OneOf(["sender", "receiver"]), required=True, default="sender")

    @post_load(pass_original=True)
    def clean_up(self, data, original: "Messages", **_kwargs):
        if original.sender_id == current_user.id:
            data["user_relation"] = "sender"
        else:
            data["user_relation"] = "receiver"
        return data


class NewMessageSchema(ImgVidSchema):
    content = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, error="Message cannot be empty"),
        ],
    )

    # noinspection PyUnusedLocal
    @post_load
    def check_content(self, data, **kwargs):  # noqa: ARG002
        if re.match(r"^\s*$", data["content"]):
            raise ValidationError("Message cannot be empty spaces", field_name="content")
        return data
