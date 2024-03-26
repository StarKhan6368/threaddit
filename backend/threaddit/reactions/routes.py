from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from threaddit.comments.models import Comments
from threaddit.posts.models import Posts
from threaddit.reactions.models import Reactions

reactions = Blueprint("reactions", __name__, url_prefix="/api")


@reactions.route("/reactions/post/<post_id>", methods=["PATCH"])
@login_required
def update_reaction_post(post_id: int):
    reaction = Reactions.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if (form := request.json) and reaction:
        reaction.patch(form.get("is_upvote"))
        return jsonify({"message": "Reaction updated"}), 200
    return jsonify({"message": "Invalid Reaction"}), 400


@reactions.route("/reactions/post/<post_id>", methods=["PUT"])
@login_required
def add_reaction_post(post_id):
    post = Posts.query.filter_by(id=post_id).first()
    if (form := request.json) and post:
        Reactions.add(user_id=current_user.id, is_upvote=form.get("is_upvote"), post=post)
        return jsonify({"message": "Reaction added"}), 200
    return jsonify({"message": "Invalid Reaction"}), 400


@reactions.route("/reactions/post/<post_id>", methods=["DELETE"])
@login_required
def delete_reaction_post(post_id):
    reaction = Reactions.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if reaction:
        reaction.remove()
        return jsonify({"message": "Reaction deleted"}), 200
    return jsonify({"message": "Invalid Reaction"}), 400


@reactions.route("/reactions/comment/<comment_id>", methods=["PATCH"])
@login_required
def update_reaction_comment(comment_id):
    reaction = Reactions.query.filter_by(comment_id=comment_id, user_id=current_user.id).first()
    if (form := request.json) and reaction:
        reaction.patch(form.get("is_upvote"))
        return jsonify({"message": "Reaction updated"}), 200
    return jsonify({"message": "Invalid Reaction"}), 400


@reactions.route("/reactions/comment/<comment_id>", methods=["PUT"])
@login_required
def add_reaction_comment(comment_id):
    comment = Comments.query.filter_by(id=comment_id).first()
    if (form := request.json) and comment and not comment.is_deleted:
        Reactions.add(user_id=current_user.id, is_upvote=form.get("is_upvote"), comment=comment)
        return jsonify({"message": "Reaction added"}), 200
    return jsonify({"message": "Invalid Reaction"}), 400


@reactions.route("/reactions/comment/<comment_id>", methods=["DELETE"])
@login_required
def delete_reaction_comment(comment_id):
    reaction = Reactions.query.filter_by(comment_id=comment_id, user_id=current_user.id).first()
    if reaction:
        reaction.remove()
        return jsonify({"message": "Reaction deleted"}), 200
    return jsonify({"message": "Invalid Reaction"}), 400
