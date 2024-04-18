from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.posts.models import Posts
from threaddit.posts.schemas import PostFeedSchema, PostFeedType, PostFormSchema, PostResponseSchema, PostSchema
from threaddit.saves.models import Saves
from threaddit.threads.models import Thread

if TYPE_CHECKING:
    from threaddit.users.models import User

posts = Blueprint("posts", __name__, url_prefix="/")
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
post_feed_schema = PostFeedSchema()
post_form_schema = PostFormSchema()
posts_resp_schema = PostResponseSchema()


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
        sa.select(Posts).where(Posts.thread_id.in_(thread_ids), query["duration"]).order_by(query["sort_by"]),
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
        sa.select(Posts).where(Posts.thread_id == thread.id, query["duration"]).order_by(query["sort_by"]),
        page=query["page"],
        per_page=query["limit"],
        error_out=False,
    )
    return posts_resp_schema.dump(posts_list), 200


@posts.route("/threads/<thread_id:thread>/posts", methods=["POST"])
@jwt_required()
def post_add(thread: "Thread"):
    form: "PostFormSchema" = post_form_schema.load(request.form | request.files)
    new_post = Posts.add(form, current_user, thread)
    db.session.commit()
    return post_schema.dump(new_post), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>", methods=["GET"])
@jwt_required(optional=True)
def post_get(thread: "Thread", post: "Posts"):
    if post.thread_id != thread.id:
        return abort(400, {"message": f"Post does not belong to thread {thread.id}"})
    return post_schema.dump(post), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>", methods=["PATCH"])
@jwt_required()
def post_update(thread: "Thread", post: "Posts"):
    if post.thread_id != thread.id:
        return abort(400, {"message": f"Post does not belong to thread {thread.id}"})
    form: "PostFormSchema" = post_form_schema.load(request.form | request.files)
    if post.user_id != current_user.id:
        return abort(403, {"message": "Unauthorized"})
    post.update(form)
    db.session.commit()
    return post_schema.dump(post), 200


@posts.route("/threads/<thread_id:thread>/posts/<post_id:post>", methods=["DELETE"])
@jwt_required()
def post_del(thread: "Thread", post: "Posts"):
    if post.thread_id != thread.id:
        return abort(400, {"message": f"Post does not belong to thread {thread.id}"})
    if post.user_id == current_user.id or current_user.is_admin or current_user.moderator_in(thread):
        post.delete()
        db.session.commit()
        return jsonify(message="Post deleted"), 200
    return abort(403, {"message": "Unauthorized"})


# noinspection DuplicatedCode
@posts.route("/users/<user_name:user>/posts", methods=["GET"])
@jwt_required(optional=True)
def user_posts_get(user: "User"):
    query: "PostFeedType" = post_feed_schema.load(request.args)
    posts_list = db.paginate(
        sa.select(Posts).where(Posts.user_id == user.id, query["duration"]).order_by(query["sort_by"]),
        page=query["page"],
        per_page=query["limit"],
        error_out=False,
    )
    return posts_resp_schema.dump(posts_list), 200


@posts.route("/users/<user_name:user>/posts/saves", methods=["GET"])
@jwt_required()
def user_saved_posts_get(user: "User"):
    if current_user.id != user.id:
        return abort(403, {"message": "Unauthorized"})
    query: "PostFeedType" = post_feed_schema.load(request.args)
    posts_list = db.paginate(
        sa.select(Posts)
        .join(Saves)
        .where(Saves.user_id == user.id, Saves.comment_id == None, query["duration"])  # noqa: E711
        .order_by(query["sort_by"]),
        page=query["page"],
        per_page=query["limit"],
        error_out=False,
    )
    return posts_resp_schema.dump(posts_list), 200
