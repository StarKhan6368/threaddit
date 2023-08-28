from threaddit.comments.models import Comments, CommentInfo
from threaddit import db
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
