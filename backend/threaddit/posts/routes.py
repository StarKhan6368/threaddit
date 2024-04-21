from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.auth.decorators import admin_mod, admin_mod_author
from threaddit.notifications.models import Notifications, NotifType
from threaddit.posts.models import Posts
from threaddit.posts.schemas import (
    PostFeedSchema,
    PostFeedType,
    PostFormSchema,
    PostFormType,
    PostResponseSchema,
    PostSchema,
)
from threaddit.reports.schemas import ResReportTypeSchema
from threaddit.saves.models import Saves
from threaddit.threads.models import Thread

if TYPE_CHECKING:
    from threaddit.users.models import User

posts = Blueprint("posts", __name__)
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
post_feed_schema = PostFeedSchema()
post_form_schema = PostFormSchema()
posts_resp_schema = PostResponseSchema()
res_report_schema = ResReportTypeSchema()


@posts.route("/feed/<feed_name>", methods=["GET"])
@jwt_required(optional=True)
def feed_get(feed_name: str):
    query: "PostFeedType" = post_feed_schema.load(request.args | {"feed_name": feed_name})

    if query["feed_name"] == "home" and not current_user:
        return abort(400, {"message": "Must be logged in to view home feed"})

    match query["feed_name"]:
        case "home":
            thread_ids = [subscription.thread_id for subscription in current_user.subscriptions]
        case "all":
            thread_ids = [
                thread.id
                for thread in db.session.scalars(sa.select(Thread).order_by(Thread.subscriber_count.desc())).all()
            ]
        case "popular":
            thread_ids = [
                thread.id for thread in db.session.scalars(sa.select(Thread).order_by(Thread.post_count.desc())).all()
            ]
        case _:
            return abort(400, {"message": "Invalid Request, Invalid Feed"})

    posts_list = db.paginate(
        sa.select(Posts)
        .where(Posts.thread_id.in_(thread_ids), query["duration"], query["spoiler"], query["nsfw"])
        .order_by(query["sort_by"]),
        page=query["page"],
        per_page=query["limit"],
        error_out=False,
    )

    return posts_resp_schema.dump(posts_list), 200


# noinspection DuplicatedCode
@posts.route("/threads/<thread_id:thread>/posts", methods=["GET"])
@jwt_required(optional=True)
def thread_posts(thread: "Thread"):
    query: "PostFeedType" = post_feed_schema.load(request.args)
    posts_list = db.paginate(
        sa.select(Posts)
        .where(Posts.thread_id == thread.id, query["duration"], query["spoiler"], query["nsfw"])
        .order_by(query["sort_by"], Posts.is_sticky.desc()),
        page=query["page"],
        per_page=query["limit"],
        error_out=False,
    )
    return posts_resp_schema.dump(posts_list), 200


@posts.route("/threads/<thread_id:thread>/posts", methods=["POST"])
@jwt_required()
def post_add(thread: "Thread"):
    if thread.is_locked:
        return abort(403, {"message": "Thread is locked"})
    form: "PostFormType" = post_form_schema.load(request.form | request.files)
    if form["is_nsfw"] and not thread.allow_nsfw:
        return abort(400, {"message": "Thread does not allow nsfw posts"})
    new_post = Posts.add(form, current_user, thread)
    db.session.commit()
    return post_schema.dump(new_post), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>", methods=["GET"])
@jwt_required(optional=True)
def post_get(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    return post_schema.dump(post), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>", methods=["PATCH"])
@jwt_required()
def post_update(thread: "Thread", post: "Posts"):
    if post.user_id != current_user.id:
        return abort(403, {"message": "Unauthorized"})
    post.validate_post(thread)
    form: "PostFormSchema" = post_form_schema.load(request.form | request.files)
    if form["is_nsfw"] and not thread.allow_nsfw:
        return abort(400, {"message": "Thread does not allow nsfw posts"})
    post.update(form)
    db.session.commit()
    return post_schema.dump(post), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>", methods=["DELETE"])
@jwt_required()
@admin_mod_author()
def post_del(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    # noinspection DuplicatedCode
    if current_user.id != post.user_id:
        report = res_report_schema.load(request.args)
        if report["report_id"].thread_id != thread.id:
            return abort(400, {"message": "Invalid Report ID"})
        Notifications.notify(
            notif_type=NotifType.POST_REMOVED,
            user=post.user,
            title=f"Your post on {thread.name} has been removed by moderator {current_user.username}",
            sub_title=f"Reason : {report['report_id'].name}",
            content=post.title,
            res_id=post.id,
            res_media_id=None,
        )
    post.delete()
    db.session.commit()
    return jsonify(message="Post deleted"), 200


# noinspection DuplicatedCode
@posts.route("/users/<user_name:user>/posts", methods=["GET"])
@jwt_required(optional=True)
def user_posts_get(user: "User"):
    query: "PostFeedType" = post_feed_schema.load(request.args)
    posts_list = db.paginate(
        sa.select(Posts)
        .where(Posts.user_id == user.id, query["duration"], query["spoiler"], query["nsfw"])
        .order_by(query["sort_by"]),
        page=query["page"],
        per_page=query["limit"],
        error_out=False,
    )
    return posts_resp_schema.dump(posts_list), 200


@posts.route("/me/posts/saves", methods=["GET"])
@jwt_required()
def user_saved_posts_get():
    query: "PostFeedType" = post_feed_schema.load(request.args)
    posts_list = db.paginate(
        sa.select(Posts)
        .join(Saves)
        .where(
            Saves.user_id == current_user.id,
            Saves.comment_id.is_(None),
            query["duration"],
            query["spoiler"],
            query["nsfw"],
        )
        .order_by(query["sort_by"]),
        page=query["page"],
        per_page=query["limit"],
        error_out=False,
    )
    return posts_resp_schema.dump(posts_list), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>/mark_nsfw", methods=["POST"])
@jwt_required()
@admin_mod_author()
def post_mark_nsfw(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    post.is_nsfw = True
    db.session.commit()
    return jsonify(message="Post Marked NSFW"), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>/unmark_nsfw", methods=["POST"])
@jwt_required()
@admin_mod_author()
def post_unmark_nsfw(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    post.is_nsfw = False
    db.session.commit()
    return jsonify(message="Post Unmarked NSFW"), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>/mark_spoiler", methods=["POST"])
@jwt_required()
@admin_mod_author()
def post_mark_spoiler(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    post.is_spoiler = True
    db.session.commit()
    return jsonify(message="Post Marked Spoiler"), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>/unmark_spoiler", methods=["POST"])
@jwt_required()
@admin_mod_author()
def post_unmark_spoiler(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    post.is_spoiler = False
    db.session.commit()
    return jsonify(message="Post Unmarked Spoiler"), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>/mark_sticky", methods=["POST"])
@jwt_required()
@admin_mod()
def post_mark_sticky(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    post.is_sticky = True
    db.session.commit()
    return jsonify(message="Post Marked Sticky"), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>/unmark_sticky", methods=["POST"])
@jwt_required()
@admin_mod()
def post_unmark_sticky(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    post.is_sticky = False
    db.session.commit()
    return jsonify(message="Post Unmarked Sticky"), 200
