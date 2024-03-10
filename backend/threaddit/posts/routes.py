from flask import Blueprint, jsonify, request
from threaddit import db
from flask_login import current_user, login_required
from threaddit.posts.models import (
    PostInfo,
    Posts,
    PostValidator,
    get_filters,
    SavedPosts,
)
from threaddit.subthreads.models import Subscription, SubthreadInfo

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
        threads = [subscription.subthread.id for subscription in Subscription.query.filter_by(user_id=current_user.id)]
    elif feed_name == "all":
        threads = (thread.id for thread in SubthreadInfo.query.order_by(SubthreadInfo.members_count.desc()).limit(25))
    elif feed_name == "popular":
        threads = (thread.id for thread in SubthreadInfo.query.order_by(SubthreadInfo.posts_count.desc()).limit(25))
    else:
        return jsonify({"message": "Invalid Request"}), 400
    post_list = [
        pinfo.as_dict(cur_user=current_user.id if current_user.is_authenticated else None)
        for pinfo in PostInfo.query.filter(PostInfo.thread_id.in_(threads))
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
    if post_info:
        return (
            jsonify({"post": post_info.as_dict()}),
            200,
        )
    return jsonify({"message": "Invalid Post"}), 400


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
    Posts.add(form_data, image, current_user.id)
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
    update_post = Posts.query.filter_by(id=pid).first()
    if not update_post:
        return jsonify({"message": "Invalid Post"}), 400
    elif update_post.user_id != current_user.id:
        return jsonify({"message": "Unauthorized"}), 401
    update_post.patch(form_data, image)
    return (
        jsonify(
            {
                "message": "Post udpated",
                "new_data": update_post.post_info[0].as_dict(current_user.id),
            }
        ),
        200,
    )


@posts.route("/post/<pid>", methods=["DELETE"])
@login_required
def delete_post(pid):
    post = Posts.query.filter_by(id=pid).first()
    if not post:
        return jsonify({"message": "Invalid Post"}), 400
    elif post.user_id == current_user.id or current_user.has_role("admin"):
        post.delete_media()
        Posts.query.filter_by(id=pid).delete()
        db.session.commit()
        return jsonify({"message": "Post deleted"}), 200
    current_user_mod_in = [r.subthread_id for r in current_user.user_role if r.role.slug == "mod"]
    if post.subthread_id in current_user_mod_in:
        post.delete_media()
        Posts.query.filter_by(id=pid).delete()
        db.session.commit()
        return jsonify({"message": "Post deleted"}), 200
    return jsonify({"message": "Unauthorized"}), 401


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
        pinfo.as_dict(current_user.id if current_user.is_authenticated else None)
        for pinfo in PostInfo.query.filter(PostInfo.thread_id == tid)
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
        pinfo.as_dict(current_user.id if current_user.is_authenticated else None)
        for pinfo in PostInfo.query.filter(PostInfo.user_name == user_name)
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
    limit = request.args.get("limit", default=20, type=int)
    offset = request.args.get("offset", default=0, type=int)
    saved_posts = SavedPosts.query.filter(SavedPosts.user_id == current_user.id).offset(offset).limit(limit).all()
    post_infos = [PostInfo.query.filter_by(post_id=pid.post_id) for pid in saved_posts]
    return (
        jsonify([p.first().as_dict(current_user.id) for p in post_infos]),
        200,
    )


@posts.route("/posts/saved/<pid>", methods=["DELETE"])
@login_required
def delete_saved(pid):
    saved_post = SavedPosts.query.filter_by(user_id=current_user.id, post_id=pid).first()
    if not saved_post:
        return jsonify({"message": "Invalid Post ID"}), 400
    SavedPosts.query.filter_by(user_id=current_user.id, post_id=pid).delete()
    db.session.commit()
    return jsonify({"message": "Saved Post deleted"}), 200


@posts.route("/posts/saved/<pid>", methods=["PUT"])
@login_required
def new_saved(pid):
    new_saved = SavedPosts(user_id=current_user.id, post_id=pid)
    db.session.add(new_saved)
    db.session.commit()
    return jsonify({"message": "Saved"}), 200
