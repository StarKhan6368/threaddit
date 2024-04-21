from typing import override

import sqlalchemy as sa
from flask import abort
from werkzeug.routing import BaseConverter

from threaddit import db
from threaddit.comments.models import Comments


class CommentConverter(BaseConverter):
    regex = r"(\d+)"

    @override
    def to_python(self, comment_id: str):
        comment: "Comments|None" = db.session.execute(sa.select(Comments).filter_by(id=comment_id)).scalar_one_or_none()
        if not comment:
            return abort(404, {"comment_id": f"Comment with ID {comment_id} not found"})
        return comment

    @override
    def to_url(self, comment_id):
        return str(comment_id)
