from typing import TYPE_CHECKING

from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.reactions.models import Reactions
from threaddit.reactions.schemas import ReactionSchema, ReactionType

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.posts.models import Posts
    from threaddit.threads.models import Thread

reactions = Blueprint("reactions", __name__)
reaction_schema = ReactionSchema()


@reactions.route("/threads/<thread_id:thread>/posts/<post_id:post>/reactions", methods=["POST"])
@jwt_required()
def post_reaction_add(thread: "Thread", post: "Posts"):
    reaction = Reactions.get_reaction(current_user, thread, post)
    args: "ReactionType" = reaction_schema.load(request.args)
    if not reaction:
        Reactions.add(is_upvote=args["is_upvote"], user=current_user, post=post)
        db.session.commit()
        return jsonify(message=f"Post has been {'upvoted' if args['is_upvote'] else 'downvoted'} "), 201
    return abort(400, {"message": "Post Reaction Already Exists"})


@reactions.route("/threads/<thread_id:thread>/posts/<post_id:post>/reactions", methods=["PATCH"])
@jwt_required()
def post_reaction_update(thread: "Thread", post: "Posts"):
    reaction = Reactions.get_reaction(current_user, thread, post)
    args: "ReactionType" = reaction_schema.load(request.args)
    if reaction:
        reaction.update(args["is_upvote"], post=post)
        db.session.commit()
        return jsonify(message=f"Post has been {'upvoted' if args['is_upvote'] else 'downvoted'} "), 201
    return abort(400, {"message": "Post Reaction Doesn't Exists"})


@reactions.route("/threads/<thread_id:thread>/posts/<post_id:post>/reactions", methods=["DELETE"])
@jwt_required()
def post_reaction_del(thread: "Thread", post: "Posts"):
    reaction = Reactions.get_reaction(current_user, thread, post)
    if reaction:
        reaction.delete(post=post)
        db.session.commit()
        return jsonify(message="Post Reaction deleted"), 200
    return abort(400, {"message": "Post Reaction Doesn't Exists"})


@reactions.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/reactions", methods=["POST"]
)
@jwt_required()
def comment_reaction_add(thread: "Thread", post: "Posts", comment: "Comments"):
    reaction = Reactions.get_reaction(current_user, thread, post, comment)
    args: "ReactionType" = reaction_schema.load(request.args)
    if reaction and not comment.is_deleted:
        Reactions.add(user=current_user, is_upvote=args["is_upvote"], post=post, comment=comment)
        db.session.commit()
        return jsonify(message=f"Comment has been {'upvoted' if args['is_upvote'] else 'downvoted'} "), 201
    return abort(400, {"message": "Comment Reaction Already Exists"})


@reactions.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/reactions", methods=["PATCH"]
)
@jwt_required()
def comment_reaction_update(thread: "Thread", post: "Posts", comment: "Comments"):
    reaction = Reactions.get_reaction(current_user, thread, post, comment)
    args: "ReactionType" = reaction_schema.load(request.args)
    if reaction:
        reaction.update(args["is_upvote"], post=post, comment=comment)
        db.session.commit()
        return jsonify(message=f"Comment has been {'upvoted' if args['is_upvote'] else 'downvoted'} "), 201
    return abort(400, {"message": "Comment Reaction Doesn't Exists"})


@reactions.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/reactions", methods=["DELETE"]
)
@jwt_required()
def comment_reaction_del(thread: "Thread", post: "Posts", comment: "Comments"):
    reaction = Reactions.get_reaction(current_user, thread, post, comment)
    if reaction:
        reaction.delete(post=post, comment=comment)
        db.session.commit()
        return jsonify(message="Comment Reaction deleted"), 200
    return abort(400, {"message": "Comment Reaction Doesn't Exists"})
