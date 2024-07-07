from apiflask import APIBlueprint

from threaddit.vote.models import Votes

votes = APIBlueprint("votes", __name__, tag="Votes", url_prefix="/votes")
