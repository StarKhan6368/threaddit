from threaddit.comments.models import Comments
from flask import Blueprint

comments = Blueprint("comments", __name__, url_prefix="/api")
