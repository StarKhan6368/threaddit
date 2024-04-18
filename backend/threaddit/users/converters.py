from typing import override

import sqlalchemy as sa
from flask import abort
from werkzeug.routing import BaseConverter

from threaddit import db
from threaddit.users.models import User


class UserConverter(BaseConverter):
    regex = r"[a-zA-Z0-9_-]+"

    @override
    def to_python(self, value: str) -> "User":
        user = db.session.scalar(sa.select(User).where(User.username == value))
        if not user:
            abort(
                404,
                {
                    "user_name": f"User with username {value} not found",
                },
            )
        return user

    @override
    def to_url(self, value: str):
        return str(value)
