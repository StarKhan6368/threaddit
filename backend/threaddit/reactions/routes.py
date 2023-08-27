from flask import Blueprint, jsonify, request
from threaddit import db
from threaddit.posts.models import Posts
from threaddit.reactions.models import Reactions
from flask_login import current_user

reactions = Blueprint("reactions", __name__, url_prefix="/api")


@reactions.route("/reactions/post/<post_id>", methods=["PATCH"])
def update_reaction_post(post_id):
    has_upvoted = request.json.get("is_upvote")
    update_reaction = Reactions.query.filter_by(
        post_id=post_id, user_id=current_user.id
    ).first()
    update_reaction.is_upvote = has_upvoted
    db.session.commit()
    return jsonify({"message": "Reaction updated"}), 200


@reactions.route("/reactions/post/<post_id>", methods=["PUT"])
def add_reaction_post(post_id):
    has_upvoted = request.json.get("is_upvote")
    new_reaction = Reactions(
        user_id=current_user.id, post_id=post_id, is_upvote=has_upvoted
    )
    db.session.add(new_reaction)
    db.session.commit()
    return jsonify({"message": "Reaction added"}), 200


@reactions.route("/reactions/post/<post_id>", methods=["DELETE"])
def delete_reaction_post(post_id):
    Reactions.query.filter_by(post_id=post_id, user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"message": "Reaction deleted"}), 200


@reactions.route("/reactions/comment/<comment_id>", methods=["PATCH"])
def update_reaction_comment(comment_id):
    has_upvoted = request.json.get("is_upvote")
    update_reaction = Reactions.query.filter_by(
        comment_id=comment_id, user_id=current_user.id
    ).first()
    update_reaction.is_upvote = has_upvoted
    db.session.commit()
    return jsonify({"message": "Reaction updated"}), 200


@reactions.route("/reactions/comment/<comment_id>", methods=["PUT"])
def add_reaction_comment(comment_id):
    has_upvoted = request.json.get("is_upvote")
    new_reaction = Reactions(
        user_id=current_user.id, comment_id=comment_id, is_upvote=has_upvoted
    )
    db.session.add(new_reaction)
    db.session.commit()
    return jsonify({"message": "Reaction added"}), 200


@reactions.route("/reactions/comment/<comment_id>", methods=["DELETE"])
def delete_reaction_comment(comment_id):
    Reactions.query.filter_by(comment_id=comment_id, user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"message": "Reaction deleted"}), 200
