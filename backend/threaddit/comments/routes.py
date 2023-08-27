from threaddit.comments.models import Comments, CommentInfo
from threaddit.posts.models import PostInfo
from flask import Blueprint, jsonify
from threaddit.comments.utils import create_comment_tree

comments = Blueprint("comments", __name__, url_prefix="/api")


@comments.route("/comments/post/<pid>", methods=["GET"])
def get_comments(pid):
    comments = (
        CommentInfo.query.filter_by(post_id=pid)
        .order_by(CommentInfo.has_parent.desc())
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
