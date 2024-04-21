from marshmallow import fields

from threaddit import ma
from threaddit.media.schemas import MediaSchema
from threaddit.notifications.models import Notifications


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notifications
        exclude = ("user_id",)

    notif_type = fields.Function(lambda notif: notif.notif_type.name)
    media = fields.Nested(MediaSchema(), dump_default=None)
