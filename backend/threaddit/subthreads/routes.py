from threaddit.subthreads.models import Subthread, SubthreadInfo, Subscription
from flask_login import current_user, login_required
from threaddit.users.models import User
from flask import Blueprint, jsonify, request
from threaddit.models import UserRole
from threaddit import db
from threaddit.auth.decorators import auth_role

threads = Blueprint("threads", __name__, url_prefix="/api")


@threads.route("/threads", methods=["GET"])
def get_subthreads():
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)
    cur_user = current_user.id if current_user.is_authenticated else None
    subscribed_threads = []
    if current_user.is_authenticated:
        subscribed_threads = [
            subscription.subthread.as_dict(cur_user)
            for subscription in Subscription.query.filter_by(user_id=current_user.id)
            .limit(limit)
            .offset(offset)
            .all()
        ]
    all_threads = [
        subinfo.as_dict()
        for subinfo in SubthreadInfo.query.filter(
            SubthreadInfo.members_count.is_not(None)
        )
        .order_by(SubthreadInfo.members_count.desc())
        .limit(limit)
        .offset(offset)
        .all()
    ]
    popular_threads = [
        subinfo.as_dict()
        for subinfo in SubthreadInfo.query.filter(
            SubthreadInfo.posts_count.is_not(None)
        )
        .order_by(SubthreadInfo.posts_count.desc())
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
    Subscription.add(tid, current_user.id)
    return jsonify({"message": "Subscribed"}), 200


@threads.route("threads/subscription/<tid>", methods=["DELETE"])
@login_required
def del_subscription(tid):
    subscription = Subscription.query.filter_by(
        user_id=current_user.id, subthread_id=tid
    ).first()
    if subscription:
        subscription.delete_logo()
        Subscription.query.filter_by(user_id=current_user.id, subthread_id=tid).delete()
        db.session.commit()
    else:
        return jsonify({"message": "Invalid Subscription"}), 400
    return jsonify({"message": "UnSubscribed"}), 200


@threads.route("/thread", methods=["POST"])
@login_required
def new_thread():
    image = request.files.get("media")
    form_data = request.form.to_dict()
    subthread = Subthread.add(form_data, image, current_user.id)
    if subthread:
        UserRole.add_moderator(current_user.id, subthread.id)
        return jsonify({"message": "Thread created"}), 200
    return jsonify({"message": "Something went wrong"}), 500


@threads.route("/thread/<tid>", methods=["PATCH"])
@login_required
@auth_role(["admin", "mod"])
def update_thread(tid):
    thread = Subthread.query.filter_by(id=tid).first()
    if not thread:
        return jsonify({"message": "Invalid Thread"}), 400
    image = request.files.get("media")
    form_data = request.form.to_dict()
    thread.patch(form_data, image)
    return jsonify({"message": "Thread updated"}), 200


@threads.route("/thread/mod/<tid>/<username>", methods=["PUT"])
@login_required
@auth_role(["admin", "mod"])
def new_mod(tid, username):
    user = User.query.filter_by(username=username).first()
    UserRole.add_moderator(user.id, tid)
    return jsonify({"message": "Moderator added"}), 200


@threads.route("/thread/mod/<tid>/<username>", methods=["DELETE"])
@login_required
@auth_role(["admin", "mod"])
def delete_mod(tid, username):
    user = User.query.filter_by(username=username).first()
    thread = Subthread.query.filter_by(id=tid).first()
    if thread.created_by == user.id and not current_user.has_role("admin"):
        return jsonify({"message": "Cannot Remove Thread Creator"}), 400
    existing_role = UserRole.query.filter_by(user_id=user.id, subthread_id=tid).delete()
    db.session.commit()
    return jsonify({"message": "Moderator deleted"}), 200
