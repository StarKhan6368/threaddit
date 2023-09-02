import os
from flask import Blueprint, jsonify, request
from threaddit import db, app
from flask_login import current_user, login_required
from threaddit.posts.models import (
    PostInfo,
    Posts,
    Reactions,
    PostValidator,
    get_filters,
    SavedPosts,
)
from threaddit.subthreads.models import Subscription, SubthreadInfo
from werkzeug.utils import secure_filename

posts = Blueprint("posts", __name__, url_prefix="/api")


@posts.route("/posts/<feed_name>", methods=["GET"])
def get_posts(feed_name):
    limit = request.args.get("limit", default=20, type=int)
    offset = request.args.get("offset", default=0, type=int)
    sortby = request.args.get("sortby", default="top", type=str)
    duration = request.args.get("duration", default="alltime", type=str)
    try:
        sortBy, durationBy = get_filters(sortby=sortby, duration=duration)
    except Exception:
        return jsonify({"message": "Invalid Request"}), 400
    if feed_name == "home" and current_user.is_authenticated:
        threads = [
            subscription.subthread.id
            for subscription in Subscription.query.filter_by(user_id=current_user.id)
        ]
    elif feed_name == "all":
        threads = (
            thread.id
            for thread in SubthreadInfo.query.order_by(
                SubthreadInfo.members_count.desc()
            ).limit(25)
        )
    elif feed_name == "popular":
        threads = (
            thread.id
            for thread in SubthreadInfo.query.order_by(
                SubthreadInfo.posts_count.desc()
            ).limit(25)
        )
    else:
        return jsonify({"message": "Invalid Request"}), 400
    post_list = [
        post.as_dict()
        for post in PostInfo.query.filter(PostInfo.thread_id.in_(threads))
        .order_by(sortBy)
        .filter(durationBy)
        .limit(limit)
        .offset(offset)
        .all()
    ]
    return jsonify(post_list), 200


@posts.route("/post/<pid>", methods=["GET"])
def get_post(pid):
    post_info = PostInfo.query.filter_by(post_id=pid).first()
    return (
        jsonify({"post": post_info.as_dict()}),
        200,
    )


@posts.route("/post", methods=["POST"])
@login_required
def new_post():
    image = request.files.get("media")
    form_data = request.form.to_dict()
    PostValidator().load(
        {
            "subthread_id": form_data.get("subthread_id"),
            "title": form_data.get("title"),
            "content": form_data.get("content"),
        }
    )
    media = None
    if form_data.get("content_type") == "image" and image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        media = filename
    elif form_data.get("content_type") == "url":
        media = form_data.get("content_url")
    new_post = Posts(
        user_id=current_user.id,
        subthread_id=form_data.get("subthread_id"),
        title=form_data.get("title"),
        media=media,
        content=form_data.get("content"),
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"message": "Post created"}), 200


@posts.route("/post/<pid>", methods=["PATCH"])
@login_required
def update_post(pid):
    image = request.files.get("media")
    form_data = request.form.to_dict()
    PostValidator().load(
        {
            "subthread_id": form_data.get("subthread_id"),
            "title": form_data.get("title"),
            "content": form_data.get("content"),
        }
    )
    media = None
    if form_data.get("content_type") == "image" and image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        media = filename
    elif form_data.get("content_type") == "url":
        media = form_data.get("content_url")
    update_post = Posts.query.filter_by(id=pid)
    if not update_post:
        return jsonify({"message": "Invalid Post"}), 400
    else:
        update_post = update_post.first()
        if update_post.user_id != current_user.id:
            return jsonify({"message": "Unauthorized"}), 401
        update_post = update_post.first()
        update_post.title = form_data.get("title")
        update_post.content = form_data.get("content")
        update_post.is_edit = True
        if media:
            update_post.media = media
    db.session.commit()
    return jsonify({"message": "Post udpated"}), 200


@posts.route("/post/<pid>", methods=["DELETE"])
@login_required
def delete_post(pid):
    post = Posts.query.filter_by(id=pid).first()
    if not post:
        return jsonify({"message": "Invalid Post"}), 400
    if not (
        post.user_id == current_user.id
        or current_user.has_role("admin")
        or current_user.has_role("mod")
    ):
        return jsonify({"message": "Unauthorized"}), 401
    elif post.user_id == current_user.id:
        Posts.query.filter_by(id=pid).delete()
        db.session.commit()
        return jsonify({"message": "Post deleted"}), 200
    current_user_mod_in = [
        r.subthread_id for r in current_user.user_role if r.role.slug == "mod"
    ]
    if post.subthread_id in current_user_mod_in or current_user.has_role("mod"):
        Posts.query.filter_by(id=pid).delete()
        db.session.commit()
    else:
        return jsonify({"message": "Unauthorized"}), 401
    return jsonify({"message": "Post deleted"}), 200


@posts.route("/posts/thread/<tid>", methods=["GET"])
def get_posts_of_thread(tid):
    limit = request.args.get("limit", default=20, type=int)
    offset = request.args.get("offset", default=0, type=int)
    sortby = request.args.get("sortby", default="top", type=str)
    duration = request.args.get("duration", default="alltime", type=str)
    try:
        sortBy, durationBy = get_filters(sortby=sortby, duration=duration)
    except Exception:
        return jsonify({"message": "Invalid Request"}), 400
    post_list = [
        post.as_dict()
        for post in PostInfo.query.filter(PostInfo.thread_id == tid)
        .order_by(sortBy)
        .filter(durationBy)
        .limit(limit)
        .offset(offset)
        .all()
    ]
    return jsonify(post_list), 200


@posts.route("/posts/user/<user_name>", methods=["GET"])
def get_posts_of_user(user_name):
    limit = request.args.get("limit", default=20, type=int)
    offset = request.args.get("offset", default=0, type=int)
    sortby = request.args.get("sortby", default="top", type=str)
    duration = request.args.get("duration", default="alltime", type=str)
    try:
        sortBy, durationBy = get_filters(sortby=sortby, duration=duration)
    except Exception:
        return jsonify({"message": "Invalid Request"}), 400
    post_list = [
        post.as_dict()
        for post in PostInfo.query.filter(PostInfo.user_name == user_name)
        .order_by(sortBy)
        .filter(durationBy)
        .limit(limit)
        .offset(offset)
        .all()
    ]
    return jsonify(post_list), 200


@posts.route("/posts/saved", methods=["GET"])
@login_required
def get_saved():
    saved_posts = SavedPosts.query.filter_by(user_id=current_user.id).all()
    post_infos = [PostInfo.query.filter_by(post_id=pid.post_id) for pid in saved_posts]
    return jsonify([p.first().as_dict() for p in post_infos]), 200


@posts.route("/posts/saved/<pid>", methods=["DELETE"])
@login_required
def delete_saved(pid):
    saved_post = SavedPosts.query.filter_by(user_id=current_user.id, post_id=pid)
    if not saved_post:
        return jsonify({"message": "Invalid Post ID"}), 400
    saved_post.delete()
    db.session.commit()
    return jsonify({"message": "Saved Post deleted"}), 200


@posts.route("/posts/saved/<pid>", methods=["PUT"])
@login_required
def new_saved(pid):
    new_saved = SavedPosts(user_id=current_user.id, post_id=pid)
    db.session.add(new_saved)
    db.session.commit()
    return jsonify({"message": "Saved"}), 200
