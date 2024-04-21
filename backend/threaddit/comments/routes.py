from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.auth.decorators import admin_mod, admin_mod_author
from threaddit.comments.models import Comments
from threaddit.comments.schemas import (
    CommentBodySchema,
    CommentBodyType,
    CommentSchema,
    CommentsPaginateSchema,
    CommentsPaginateType,
    CommentsResponseSchema,
)
from threaddit.notifications.models import Notifications, NotifType
from threaddit.reports.schemas import ResReportTypeSchema
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
res_report_schema = ResReportTypeSchema()


@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments", methods=["POST"])
@jwt_required()
def post_comment_add(thread: "Thread", post: "Posts"):
    if post.is_locked:
        return abort(403, {"message": "Post is locked"})
    post.validate_post(thread)
    data: "CommentBodyType" = comment_body_schema.load(request.form | request.files)
    comment: "Comments" = Comments.add(data, user=current_user, post=post, thread=thread)
    db.session.commit()
    return comment_schema.dump(comment), 201


@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>", methods=["GET"])
@jwt_required(optional=True)
def post_comment_get(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    return comment_schema.dump(comment), 200


@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>", methods=["PATCH"])
@jwt_required()
def post_comment_update(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    body: "CommentBodyType" = comment_body_schema.load(request.form | request.files)
    if comment.user_id == current_user.id:
        comment.update(body)
        db.session.commit()
        return comment_schema.dump(comment), 200
    return abort(403, {"error": "Unauthorized", "message": "Only the author can update this comment"})


@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>", methods=["DELETE"])
@jwt_required()
@admin_mod_author()
def post_comment_delete(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    if comment.is_deleted:
        return abort(400, {"message": "Comment already deleted"})
    comment.delete(post=post, thread=thread, user=current_user)
    # noinspection DuplicatedCode
    if current_user.id != comment.user_id:
        report = res_report_schema.load(request.args)
        if report["report_id"].thread_id != thread.id:
            return abort(400, {"message": "Invalid Report ID"})
        Notifications.notify(
            notif_type=NotifType.COMMENT_REMOVED,
            user=post.user,
            title=f"Your comment on {thread.name} has been removed by moderator {current_user.username}",
            sub_title=f"Reason : {report['report_id'].name}",
            content=comment.content,
            res_id=post.id,
            res_media_id=None,
        )
    db.session.commit()
    return jsonify(message="Comment deleted"), 200


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/replies", methods=["POST"]
)
@jwt_required()
def comment_reply_add(thread: "Thread", post: "Posts", comment: "Comments"):
    if post.is_locked:
        return abort(403, {"message": "Post is locked"})
    if comment.is_locked:
        return abort(403, {"message": "Comment is locked"})
    comment.validate_comment(thread, post)
    data: "CommentBodyType" = comment_body_schema.load(request.form | request.files)
    reply: "Comments" = comment.add(data, user=current_user, post=post, comment=comment, thread=thread)
    return comment_schema.dump(reply), 201


# noinspection DuplicatedCode
@comments.route("/users/<user_name:user>/comments", methods=["GET"])
@jwt_required(optional=True)
def user_comments_get(user: "User"):
    args: "CommentsPaginateType" = comment_paginate_schema.load(request.args)
    query = (
        sa.select(Comments).where(Comments.user_id == user.id, Comments.parent_id.is_(None)).order_by(args["sort_by"])
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
        .where(Comments.thread_id == thread.id, Comments.parent_id.is_(None))
        .order_by(args["sort_by"])
    )
    pagination = db.paginate(query, page=args["page"], per_page=args["limit"], error_out=False)
    return comments_resp_schema.dump(pagination), 200


# noinspection DuplicatedCode
@comments.route("/threads/<thread_id:thread>/posts/<post_id:post>/comments", methods=["GET"])
@jwt_required(optional=True)
def post_comments_get(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    args: "CommentsPaginateType" = comment_paginate_schema.load(request.args)
    query = (
        sa.select(Comments)
        .where(Comments.post_id == post.id, Comments.parent_id.is_(None))
        .order_by(args["sort_by"], Comments.is_sticky.desc())
    )
    pagination = db.paginate(query, page=args["page"], per_page=args["limit"], error_out=False)
    return comments_resp_schema.dump(pagination), 200


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/replies", methods=["GET"]
)
@jwt_required(optional=True)
def comment_replies_get(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    args: "CommentsPaginateType" = comment_paginate_schema.load(request.args)
    query = (
        sa.select(Comments).where(Comments.parent_id == comment.id).order_by(Comments.parent_id.asc(), args["sort_by"])
    )
    pagination = db.paginate(query, page=args["page"], per_page=args["limit"], error_out=False)
    return comments_resp_schema.dump(pagination), 200


@comments.route("/me/comments/saves", methods=["GET"])
@jwt_required()
def user_saved_comments_get():
    query: "CommentsPaginateType" = comment_paginate_schema.load(request.args)
    comments_list = db.paginate(
        sa.select(Comments)
        .join(Saves)
        .where(Saves.user_id == current_user.id, Saves.comment_id.is_(None))
        .order_by(Comments.parent_id.asc(), query["sort_by"]),
        page=query["page"],
        per_page=query["limit"],
        error_out=False,
    )
    return comments_resp_schema.dump(comments_list), 200


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/mark_spoiler", methods=["POST"]
)
@jwt_required()
@admin_mod_author()
def comment_mark_spoiler(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    comment.is_spoiler = True
    db.session.commit()
    return jsonify(message="Comment Marked Spoiler"), 200


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/unmark_spoiler", methods=["POST"]
)
@jwt_required()
@admin_mod_author()
def comment_unmark_spoiler(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    comment.is_spoiler = False
    db.session.commit()
    return jsonify(message="Comment Unmarked Spoiler"), 200


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/mark_nsfw", methods=["POST"]
)
@jwt_required()
@admin_mod_author()
def comment_mark_nsfw(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    comment.is_nsfw = True
    db.session.commit()
    return jsonify(message="Comment Marked NSFW"), 200


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/unmark_nsfw", methods=["POST"]
)
@jwt_required()
@admin_mod_author()
def comment_unmark_nsfw(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    comment.is_nsfw = False
    db.session.commit()
    return jsonify(message="Comment Unmarked NSFW"), 200


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/mark_sticky", methods=["POST"]
)
@jwt_required()
@admin_mod()
def comment_mark_sticky(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    comment.is_sticky = True
    db.session.commit()
    return jsonify(message="Comment Marked Sticky"), 200


@comments.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/unmark_sticky", methods=["POST"]
)
@jwt_required()
@admin_mod_author()
def comment_unmark_sticky(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    comment.is_sticky = False
    db.session.commit()
    return jsonify(message="Comment Unmarked Sticky"), 200
