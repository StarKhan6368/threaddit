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
    if not comments:
        return jsonify({"message": "Invalid Post ID"}), 400
    cur_user = current_user.id if current_user.is_authenticated else None
    return (
        jsonify(
            {
                "post_info": PostInfo.query.filter_by(post_id=pid)
                .first()
                .as_dict(cur_user),
                "comment_info": create_comment_tree(
                    comments=comments, cur_user=cur_user
                ),
            }
        ),
        200,
    )


@comments.route("/comments/<cid>", methods=["PATCH"])
@login_required
def update_comment(cid):
    comment = Comments.query.filter_by(id=cid).first()
    if not comment:
        return jsonify({"message": "Invalid Comment"}), 400
    if comment.user_id == current_user.id:
        comment.patch(request.json.get("content"))
        return jsonify({"message": "Comment updated"}), 200
    return jsonify({"message": "Unauthorized"}), 401


@comments.route("/comments/<cid>", methods=["DELETE"])
@login_required
def delete_comment(cid):
    comment = Comments.query.filter_by(id=cid).first()
    if not comment:
        return jsonify({"message": "Invalid Comment"}), 400
    elif comment.user_id == current_user.id or current_user.has_role("admin"):
        Comments.query.filter_by(id=cid).delete()
        db.session.commit()
        return jsonify({"message": "Comment deleted"}), 200
    current_user_mod_in = [
        r.subthread_id for r in current_user.user_role if r.role.slug == "mod"
    ]
    if comment.post.subthread_id in current_user_mod_in:
        Comments.query.filter_by(id=cid).delete()
        db.session.commit()
        return jsonify({"message": "Comment deleted"}), 200
    return jsonify({"message": "Unauthorized"}), 401


@comments.route("/comments", methods=["POST"])
@login_required
def new_comment():
    form_data = request.json
    new_comment = Comments.add(form_data, current_user.id)
    return (
        jsonify(
            {
                "message": "Comment created",
                "new_comment": {"comment": new_comment, "children": []},
            }
        ),
        200,
    )
