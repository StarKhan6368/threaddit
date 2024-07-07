from apiflask import APIBlueprint

from threaddit.post.models import Posts

posts = APIBlueprint("posts", __name__, tag="Posts", url_prefix="/posts")
