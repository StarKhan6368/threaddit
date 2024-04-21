from typing import override

import sqlalchemy as sa
from flask import abort
from werkzeug.routing import BaseConverter

from threaddit import db
from threaddit.moderations.models import ModAdminInv


class InvConverter(BaseConverter):
    regex = r"[0-9]+"

    @override
    def to_python(self, value: str) -> "ModAdminInv":
        inv = db.session.scalar(sa.select(ModAdminInv).where(ModAdminInv.id == value))
        if not inv:
            abort(404, {"inv_id": f"Invitation with ID {value} not found"})
        return inv

    @override
    def to_url(self, value: str | int) -> str:
        return str(value)
