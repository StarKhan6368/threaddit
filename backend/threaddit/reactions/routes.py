from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.reactions.models import Reactions
from threaddit.reactions.schemas import ReactionSchema, ReactionType

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.posts.models import Posts

reactions = Blueprint("reactions", __name__)
reaction_schema = ReactionSchema()


@reactions.route("/posts/<post_id:post>/reactions", methods=["POST"])
@jwt_required()
def add_reaction_post(post: "Posts"):
    body: "ReactionType" = reaction_schema.load(request.json)
    reaction = db.session.scalar(
        sa.select(Reactions).where(Reactions.post_id == post.id, Reactions.user_id == current_user.id)
    )
    if not reaction:
        Reactions.add(is_upvote=body["is_upvote"], user=current_user, post=post)
        db.session.commit()
        return jsonify(message="Reaction added"), 201
    return abort(400, {"message": "Reaction Already Exists"})


@reactions.route("/posts/<post_id:post>/reactions", methods=["PATCH"])
@jwt_required()
def update_reaction_post(post: "Posts"):
    body: "ReactionType" = reaction_schema.load(request.json)
    reaction = db.session.scalar(
        sa.select(Reactions).where(Reactions.post_id == post.id, Reactions.user_id == current_user.id)
    )
    if reaction:
        reaction.update(body["is_upvote"], post=post)
        db.session.commit()
        return jsonify(message="Reaction updated"), 204
    return abort(400, {"message": "Reaction Does Not Exist"})


@reactions.route("/posts/<post_id:post>/reactions", methods=["DELETE"])
@jwt_required()
def delete_reaction_post(post: "Posts"):
    reaction = db.session.scalar(
        sa.select(Reactions).where(Reactions.post_id == post.id, Reactions.user_id == current_user.id)
    )
    if reaction:
        reaction.delete(post=post)
        db.session.commit()
        return jsonify(message="Reaction deleted"), 200
    return abort(400, {"message": "Reaction Does Not Exist"})


@reactions.route("/posts/<post_id:post>/comments/<comment_id:comment>/reactions", methods=["POST"])
@jwt_required()
def add_reaction_comment(post: "Posts", comment: "Comments"):
    body: "ReactionType" = reaction_schema.load(request.json)
    reaction = db.session.scalar(
        sa.select(Reactions).where(Reactions.comment_id == comment.id, Reactions.user_id == current_user.id)
    )
    if reaction and not comment.is_deleted:
        Reactions.add(user=current_user, is_upvote=body["is_upvote"], post=post, comment=comment)
        db.session.commit()
        return jsonify(message="Reaction added"), 200
    return abort(400, {"message": "Reaction Already Exists or Comment Deleted"})


@reactions.route("/posts/<post_id:post>/comments/<comment_id:comment>/reactions", methods=["PATCH"])
@jwt_required()
def update_reaction_comment(post: "Posts", comment: "Comments"):
    body: "ReactionType" = reaction_schema.load(request.json)
    reaction = db.session.scalar(
        sa.select(Reactions).where(Reactions.comment_id == comment.id, Reactions.user_id == current_user.id)
    )
    if reaction:
        reaction.update(body["is_upvote"], post=post, comment=comment)
        db.session.commit()
        return jsonify(message="Reaction updated"), 200
    return abort(400, {"message": "Reaction Doesn't Exists"})


@reactions.route("/posts/<post_id:post>/comments/<comment_id:comment>/reactions", methods=["DELETE"])
@jwt_required()
def delete_reaction_comment(post: "Posts", comment: "Comments"):
    reaction = db.session.scalar(
        sa.select(Reactions).where(Reactions.comment_id == comment.id, Reactions.user_id == current_user.id)
    )
    if reaction:
        reaction.delete(post=post, comment=comment)
        db.session.commit()
        return jsonify(message="Reaction deleted"), 200
    return abort(400, {"message": "Reaction Doesn't Exists"})
