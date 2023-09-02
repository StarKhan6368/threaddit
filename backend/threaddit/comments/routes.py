from threaddit.comments.models import Comments, CommentInfo
from threaddit import db
from threaddit.models import UserRole
from threaddit.posts.models import PostInfo
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from threaddit.comments.utils import create_comment_tree

comments = Blueprint("comments", __name__, url_prefix="/api")


@comments.route("/comments/post/<pid>", methods=["GET"])
def get_comments(pid):
    comments = (
        CommentInfo.query.filter_by(post_id=pid)
        .order_by(CommentInfo.has_parent.desc(), CommentInfo.comment_id)
        .all()
    )
    return (
        jsonify(
            {
                "post_info": PostInfo.query.filter_by(post_id=pid).first().as_dict(),
                "comment_info": create_comment_tree(comments=comments),
            }
        ),
        200,
    )


@comments.route("/comments/<cid>", methods=["PATCH"])
@login_required
def update_comment(cid):
    comment = Comments.query.filter_by(id=cid)
    if not comment:
        return jsonify({"message": "Invalid Comment"}), 400
    comment = comment.first()
    current_user_role = UserRole.query.filter_by(
        user_id=current_user.id, subthread_id=comment.post_id
    )
    if not comment.user_id == current_user.id or not current_user:
        return jsonify({"message": "Unauthorized"}), 401
    comment.content = request.json.get("content")
    db.session.commit()
    return jsonify({"message": "Comment updated"}), 200


@comments.route("/comments/<cid>", methods=["DELETE"])
@login_required
def delete_comment(cid):
    comment = Comments.query.filter_by(id=cid)
    if not comment:
        return jsonify({"message": "Invalid Comment"}), 400
    comment = comment.first()
    current_user_role = UserRole.query.filter_by(
        user_id=current_user.id, subthread_id=comment.post_id
    )
    if not (
        comment.user_id == current_user.id
        or current_user_role
        or current_user.has_role("admin")
    ):
        return jsonify({"message": "Unauthorized"}), 401
    Comments.query.filter_by(id=cid).delete()
    db.session.commit()
    return jsonify({"message": "Comment deleted"}), 200


@comments.route("/comments", methods=["POST"])
@login_required
def make_new_comment():
    form_data = request.json
    if form_data.get("has_parent", False):
        new_comment = Comments(
            user_id=current_user.id,
            content=form_data["content"],
            post_id=form_data["post_id"],
            has_parent=True,
            parent_id=form_data["parent_id"],
        )
    else:
        new_comment = Comments(
            user_id=current_user.id,
            content=form_data["content"],
            post_id=form_data["post_id"],
        )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({"message": "Comment created"}), 200
