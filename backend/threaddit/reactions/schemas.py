from typing import TypedDict

from marshmallow import fields

from threaddit import ma


class ReactionType(TypedDict):
    is_upvote: bool


class ReactionSchema(ma.Schema):
    is_upvote = fields.Bool(required=True)
