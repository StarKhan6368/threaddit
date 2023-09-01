from threaddit.subthreads.models import Subthread, SubthreadInfo, Subscription
from flask_login import current_user, login_required
from flask import Blueprint, jsonify, request
from threaddit import db, app
from werkzeug.utils import secure_filename
import os

threads = Blueprint("threads", __name__, url_prefix="/api")


@threads.route("/threads", methods=["GET"])
def get_subthreads():
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)
    subscribed_threads = []
    if current_user.is_authenticated:
        subscribed_threads = [
            subscription.subthread.as_dict()
            for subscription in Subscription.query.filter_by(user_id=current_user.id)
            .limit(limit)
            .offset(offset)
            .all()
        ]
    all_threads = [
        thread.as_dict()
        for thread in SubthreadInfo.query.order_by(SubthreadInfo.members_count.desc())
        .limit(limit)
        .offset(offset)
        .all()
    ]
    popular_threads = [
        thread.as_dict()
        for thread in SubthreadInfo.query.order_by(SubthreadInfo.posts_count.desc())
        .limit(limit)
        .offset(offset)
        .all()
    ]
    return (
        jsonify(
            {
                "subscribed": subscribed_threads,
                "all": all_threads,
                "popular": popular_threads,
            }
        ),
        200,
    )


@threads.route("/threads/search/<thread_name>", methods=["GET"])
def subthread_search(thread_name):
    thread_name = f"%{thread_name}%"
    subthread_list = [
        subthread.as_dict()
        for subthread in SubthreadInfo.query.filter(
            SubthreadInfo.name.ilike(thread_name)
        ).all()
    ]
    return jsonify(subthread_list), 200


@threads.route("/threads/get/all")
def get_all_thread():
    threads = Subthread.query.order_by(Subthread.name).all()
    return jsonify([t.as_dict() for t in threads]), 200


@threads.route("/threads/<thread_name>")
def get_thread_by_name(thread_name):
    thread_info = SubthreadInfo.query.filter_by(name=f"t/{thread_name}").first()
    subthread = Subthread.query.filter_by(name=f"t/{thread_name}").first()
    if not thread_info:
        return jsonify({"message": "Thread not found"}), 404
    return (
        jsonify(
            {
                "threadData": thread_info.as_dict()
                | subthread.as_dict(
                    current_user.id if current_user.is_authenticated else None
                )
            }
        ),
        200,
    )


@threads.route("threads/subscription/<tid>", methods=["POST"])
@login_required
def new_subscription(tid):
    new_sub = Subscription(current_user.id, tid)
    db.session.add(new_sub)
    db.session.commit()
    return jsonify({"message": "Subscribed"}), 200


@threads.route("threads/subscription/<tid>", methods=["DELETE"])
@login_required
def del_subscription(tid):
    subscription = Subscription.query.filter_by(
        user_id=current_user.id, subthread_id=tid
    )
    if subscription:
        subscription.delete()
        db.session.commit()
    else:
        return jsonify({"message": "Invalid Subscription"}), 400
    return jsonify({"message": "UnSubscribed"}), 200


@threads.route("/thread", methods=["POST"])
@login_required
def new_thread():
    image = request.files.get("media")
    form_data = request.form.to_dict()
    if form_data.get("content_type") == "image" and image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        media = filename
    elif form_data.get("content_type") == "url":
        media = form_data.get("content_url")
    else:
        media = None
    new_sub = Subthread(
        name=form_data.get("name")
        if form_data.get("name").startswith("t/")
        else f"t/{form_data.get('name')}",
        description=form_data.get("description"),
        logo=media,
        created_by=current_user.id,
    )
    db.session.add(new_sub)
    db.session.commit()
    return jsonify({"message": "Thread created"}), 200
