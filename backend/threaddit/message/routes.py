from apiflask import APIBlueprint

from threaddit.message.models import Messages

messages = APIBlueprint("messages", __name__, tag="Messages", url_prefix="/messages")
