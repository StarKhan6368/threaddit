from apiflask import APIBlueprint

from threaddit.media.models import Media, MediaType

media = APIBlueprint("media", __name__, tag="Media", url_prefix="/media")
