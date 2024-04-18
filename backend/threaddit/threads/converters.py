from typing import override

import sqlalchemy as sa
from flask import abort
from werkzeug.routing import BaseConverter

from threaddit import db
from threaddit.threads.models import Thread


class ThreadConverter(BaseConverter):
    regex = r"[0-9]+"

    @override
    def to_python(self, value: str) -> "Thread":
        thread = db.session.scalar(sa.select(Thread).where(Thread.id == value))
        if not thread:
            abort(404, {"thread_id": f"Thread with ID {value} not found"})
        return thread

    @override
    def to_url(self, value):
        return str(value)
