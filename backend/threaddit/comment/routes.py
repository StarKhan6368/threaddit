from apiflask import APIBlueprint

from threaddit.comment.models import Comments

comments = APIBlueprint("comments", __name__, tag="Comments", url_prefix="/comments")
