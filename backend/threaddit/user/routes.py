from apiflask import APIBlueprint

from threaddit.user.models import Users

users = APIBlueprint("users", __name__, tag="Users", url_prefix="/users")
