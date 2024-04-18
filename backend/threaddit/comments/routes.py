from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.comments.models import Comments
from threaddit.comments.schemas import (
    CommentBodySchema,
    CommentBodyType,
    CommentSchema,
    CommentsPaginateSchema,
    CommentsPaginateType,
    CommentsResponseSchema,
)
from threaddit.saves.models import Saves

if TYPE_CHECKING:
    from threaddit.posts.models import Posts
    from threaddit.threads.models import Thread
    from threaddit.users.models import User

comments = Blueprint("comments", __name__)
comment_schema = CommentSchema()
comments_resp_schema = CommentsResponseSchema()
comment_paginate_schema = CommentsPaginateSchema()
comment_body_schema = CommentBodySchema()


@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments", methods=["POST"])
@jwt_required()
def post_comment_add(thread: "Thread", post: "Posts"):
    if thread.id != post.thread_id:
        return abort(400, {"message": f"Post {post.id} not found in thread {thread.id}"})
    data: "CommentBodyType" = comment_body_schema.load(request.form | request.files)
    comment: "Comments" = Comments.add(data, user=current_user, post=post, thread=thread)
    db.session.commit()
    return comment_schema.dump(comment), 201


@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>", methods=["GET"])
@jwt_required()
def post_comment_get(thread: "Thread", post: "Posts", comment: "Comments"):
    if thread.id != post.thread_id or post.id != comment.post_id:
        return abort(404, {"message": f"Comment not found in thread {thread.id} and post {post.id}"})
    return comment_schema.dump(comment), 200


@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>", methods=["PATCH"])
@jwt_required()
def post_comment_update(thread: "Thread", post: "Posts", comment: "Comments"):
    if thread.id != post.thread_id or post.id != comment.post_id:
        return abort(404, {"message": f"Comment not found in thread {thread.id} and post {post.id}"})
    body: "CommentBodyType" = comment_body_schema.load(request.form | request.files)
    if comment.user_id == current_user.id:
        comment.update(body)
        db.session.commit()
        return comment_schema.dump(comment), 200
    return abort(403, {"error": "Unauthorized", "message": "Only the author can update this comment"})


@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>", methods=["DELETE"])
@jwt_required()
def post_comment_delete(thread: "Thread", post: "Posts", comment: "Comments"):
    if thread.id != post.thread_id or post.id != comment.post_id:
        return abort(404, {"message": f"Comment not found in thread {thread.id} and post {post.id}"})
    if comment.user_id == current_user.id or current_user.is_admin or current_user.moderator_in(thread):
        comment.delete(post=post, thread=thread, user=current_user)
        db.session.commit()
        return jsonify(message="Comment deleted"), 200
    return abort(
        403,
        {
            "error": "Unauthorized",
            "message": f"Only author, admin and {thread.name} moderators can delete this comment",
        },
    )


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/replies", methods=["POST"]
)
@jwt_required()
def comment_reply_add(thread: "Thread", post: "Posts", comment: "Comments"):
    if thread.id != post.thread_id or post.id != comment.post_id:
        return abort(404, {"message": f"Comment not found in thread {thread.id} and post {post.id}"})
    data: "CommentBodyType" = comment_body_schema.load(request.form | request.files)
    reply: "Comments" = comment.add(data, user=current_user, post=post, comment=comment, thread=thread)
    return comment_schema.dump(reply), 201


# noinspection DuplicatedCode
@comments.route("/users/<user_name:user>/comments", methods=["GET"])
def user_comments_get(user: "User"):
    args: "CommentsPaginateType" = comment_paginate_schema.load(request.args)
    query = (
        sa.select(Comments)
        .where(Comments.user_id == user.id, Comments.parent_id == None)  # noqa: E711
        .order_by(args["sort_by"])
        .limit(args["limit"])
        .offset(args["offset"])
    )
    pagination = db.paginate(query, page=args["page"], per_page=args["limit"], error_out=False)
    return comments_resp_schema.dump(pagination), 200


# noinspection DuplicatedCode
@comments.route("/threads/<thread_id:thread>/comments", methods=["GET"])
@jwt_required(optional=True)
def thread_comments_get(thread: "Thread"):
    args: "CommentsPaginateType" = comment_paginate_schema.load(request.args)
    query = (
        sa.select(Comments)
        .where(Comments.thread_id == thread.id, Comments.parent_id == None)  # noqa: E711
        .order_by(args["sort_by"])
        .limit(args["limit"])
        .offset(args["offset"])
    )
    pagination = db.paginate(query, page=args["page"], per_page=args["limit"], error_out=False)
    return comments_resp_schema.dump(pagination), 200


# noinspection DuplicatedCode
@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments", methods=["GET"])
@jwt_required(optional=True)
def post_comments_get(thread: "Thread", post: "Posts"):
    if post.thread_id != thread.id:
        return abort(404, {"message": f"Post {post.id} not found in thread {thread.id}"})
    args: "CommentsPaginateType" = comment_paginate_schema.load(request.args)
    query = (
        sa.select(Comments)
        .where(Comments.post_id == post.id, Comments.parent_id == None)  # noqa: E711
        .order_by(args["sort_by"])
        .limit(args["limit"])
        .offset(args["offset"])
    )
    pagination = db.paginate(query, page=args["page"], per_page=args["limit"], error_out=False)
    return comments_resp_schema.dump(pagination), 200


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/replies", methods=["GET"]
)
@jwt_required(optional=True)
def comment_replies_get(thread: "Thread", post: "Posts", comment: "Comments"):
    if thread.id != post.thread_id or post.id != comment.post_id:
        return abort(404, {"message": f"Comment {comment.id} not found in thread {thread.id} and post {post.id}"})
    args: "CommentsPaginateType" = comment_paginate_schema.load(request.args)
    query = (
        sa.select(Comments)
        .where(Comments.parent_id == comment.id)
        .order_by(Comments.parent_id.asc(), args["sort_by"])
        .limit(args["limit"])
        .offset(args["offset"])
    )
    pagination = db.paginate(query, page=args["page"], per_page=args["limit"], error_out=False)
    return comments_resp_schema.dump(pagination), 200


@comments.route("/users/<user_name:user>/comments/saves", methods=["GET"])
@jwt_required()
def user_saved_posts_get(user: "User"):
    if current_user.id != user.id:
        return abort(403, {"message": "Unauthorized"})
    query: "CommentsPaginateType" = comment_paginate_schema.load(request.args)
    comments_list = db.paginate(
        sa.select(Comments)
        .join(Saves)
        .where(Saves.user_id == user.id, Saves.comment_id != None)  # noqa: E711
        .order_by(Comments.parent_id.asc(), query["sort_by"]),
        page=query["page"],
        per_page=query["limit"],
        error_out=False,
    )
    return comments_resp_schema.dump(comments_list), 200
