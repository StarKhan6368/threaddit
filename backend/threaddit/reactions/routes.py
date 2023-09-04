from flask import Blueprint, jsonify, request
from threaddit import db
from threaddit.posts.models import Posts
from threaddit.reactions.models import Reactions
from flask_login import current_user, login_required

reactions = Blueprint("reactions", __name__, url_prefix="/api")


@reactions.route("/reactions/post/<post_id>", methods=["PATCH"])
@login_required
def update_reaction_post(post_id):
    has_upvoted = request.json.get("is_upvote")
    update_reaction = Reactions.query.filter_by(
        post_id=post_id, user_id=current_user.id
    ).first()
    update_reaction.is_upvote = has_upvoted
    db.session.commit()
    return jsonify({"message": "Reaction updated"}), 200


@reactions.route("/reactions/post/<post_id>", methods=["PUT"])
@login_required
def add_reaction_post(post_id):
    has_upvoted = request.json.get("is_upvote")
    Reactions.add(user_id=current_user.id, is_upvote=has_upvoted, post_id=post_id)
    return jsonify({"message": "Reaction added"}), 200


@reactions.route("/reactions/post/<post_id>", methods=["DELETE"])
@login_required
def delete_reaction_post(post_id):
    reaction = Reactions.query.filter_by(
        post_id=post_id, user_id=current_user.id
    ).first()
    if reaction:
        Reactions.query.filter_by(post_id=post_id, user_id=current_user.id).delete()
        db.session.commit()
        return jsonify({"message": "Reaction deleted"}), 200
    return jsonify({"message": "Invalid Reaction"}), 400


@reactions.route("/reactions/comment/<comment_id>", methods=["PATCH"])
@login_required
def update_reaction_comment(comment_id):
    has_upvoted = request.json.get("is_upvote")
    reaction = Reactions.query.filter_by(
        comment_id=comment_id, user_id=current_user.id
    ).first()
    if reaction:
        reaction.patch(has_upvoted)
        return jsonify({"message": "Reaction updated"}), 200
    return jsonify({"message": "Invalid Reaction"}), 400


@reactions.route("/reactions/comment/<comment_id>", methods=["PUT"])
@login_required
def add_reaction_comment(comment_id):
    has_upvoted = request.json.get("is_upvote")
    Reactions.add(user_id=current_user.id, is_upvote=has_upvoted, comment_id=comment_id)
    return jsonify({"message": "Reaction added"}), 200


@reactions.route("/reactions/comment/<comment_id>", methods=["DELETE"])
@login_required
def delete_reaction_comment(comment_id):
    reaction = Reactions.query.filter_by(
        comment_id=comment_id, user_id=current_user.id
    ).first()
    if reaction:
        Reactions.query.filter_by(
            comment_id=comment_id, user_id=current_user.id
        ).delete()
        db.session.commit()
        return jsonify({"message": "Reaction deleted"}), 200
    return jsonify({"message": "Invalid Reaction"}), 400
