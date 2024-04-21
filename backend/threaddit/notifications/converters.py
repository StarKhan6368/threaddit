from typing import override

import sqlalchemy as sa
from flask import abort
from werkzeug.routing import BaseConverter

from threaddit import db
from threaddit.notifications.models import Notifications


class NotificationConverter(BaseConverter):
    regex = r"[0-9]+"

    @override
    def to_python(self, value: str) -> "Notifications":
        notif = db.session.scalar(sa.select(Notifications).where(Notifications.id == value))
        if not notif:
            abort(404, {"notification_id": f"Notification with ID {value} not found"})
        return notif

    @override
    def to_url(self, value: str | int) -> str:
        return str(value)
