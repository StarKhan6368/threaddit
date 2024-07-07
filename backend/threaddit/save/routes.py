from apiflask import APIBlueprint

from threaddit.save.models import Saves

saves = APIBlueprint("saves", __name__, tag="Saves", url_prefix="/saves")
