from apiflask import APIBlueprint

from threaddit.thread.models import Threads

threads = APIBlueprint("threads", __name__, tag="Threads", url_prefix="/threads")
