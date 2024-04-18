from typing import TYPE_CHECKING

from flask import Blueprint, abort, jsonify
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.saves.models import Saves

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.posts.models import Posts
    from threaddit.threads.models import Thread

saves = Blueprint("saves", __name__)


@saves.route("/threads/<thread_id:thread>/posts/<post_id:post>/saves", methods=["POST"])
@jwt_required()
def user_saved_post_add(thread: "Thread", post: "Posts"):
    saved_post = Saves.get_save(current_user, thread, post)
    if saved_post:
        return abort(400, {"message": "Post already saved"})
    Saves.add(current_user, post)
    db.session.commit()
    return jsonify(message="Post saved"), 200


@saves.route("/threads/<thread_id:thread>/posts/<post_id:post>/saves", methods=["DELETE"])
@jwt_required()
def user_saved_post_del(thread: "Thread", post: "Posts"):
    saved_post = Saves.get_save(current_user, thread, post)
    if not saved_post:
        abort(400, {"message": "Post not saved"})
    saved_post.delete(post)
    db.session.commit()
    return jsonify(message="Post unsaved"), 200


@saves.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/saves", methods=["POST"])
@jwt_required()
def user_saved_comment_add(thread: "Thread", post: "Posts", comment: "Comments"):
    saved_comment = Saves.get_save(current_user, thread, post, comment)
    if saved_comment:
        return abort(400, {"message": "Comment already saved"})
    Saves.add(current_user, post, comment)
    db.session.commit()
    return jsonify(message="Comment saved"), 200


@saves.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/saves", methods=["DELETE"])
@jwt_required()
def user_saved_comment_del(thread: "Thread", post: "Posts", comment: "Comments"):
    saved_comment = Saves.get_save(current_user, thread, post, comment)
    if not saved_comment:
        abort(400, {"message": "Comment not saved"})
    saved_comment.delete(post,comment)
    db.session.commit()
    return jsonify(message="Comment unsaved"), 200
