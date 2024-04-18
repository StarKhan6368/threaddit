from typing import override

import sqlalchemy as sa
from flask import abort
from werkzeug.routing import BaseConverter

from threaddit import db
from threaddit.messages.models import Messages


class MessageConverter(BaseConverter):
    regex = r"\d+"

    @override
    def to_python(self, value: str):
        message = db.session.scalar(sa.select(Messages).where(Messages.id == value))
        if not message:
            abort(404, {"message_id": f"Message with ID {value} not found"})
        return message

    @override
    def to_url(self, value):
        return str(value)
