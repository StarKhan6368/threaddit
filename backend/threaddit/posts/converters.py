from typing import override

import sqlalchemy as sa
from flask import abort
from werkzeug.routing import BaseConverter

from threaddit import db
from threaddit.posts.models import Posts


class PostConverter(BaseConverter):
    regex = r"[0-9]+"

    @override
    def to_python(self, post_id: str):
        post = db.session.scalar(sa.select(Posts).where(Posts.id == post_id))
        if not post:
            abort(404, {"post_id": f"Post with ID {post_id} not found"})
        return post

    @override
    def to_url(self, post_id):
        return str(post_id)
