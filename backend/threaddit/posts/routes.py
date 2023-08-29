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
