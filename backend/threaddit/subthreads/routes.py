from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from threaddit import db
from threaddit.auth.decorators import auth_role
from threaddit.models import UserRole
from threaddit.subthreads.models import Subscription, Subthread
from threaddit.users.models import User

threads = Blueprint("threads", __name__, url_prefix="/api")


@threads.route("/threads", methods=["GET"])
def get_subthreads():
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)
    cur_user = current_user.id if current_user.is_authenticated else None
    subscribed_threads = []
    if cur_user:
        subscribed_threads = [sup.subthread.as_dict() for sup in current_user.subscription]
    all_threads = [
        sub.as_dict()
        for sub in Subthread.query.order_by(Subthread.subscriber_count.desc()).limit(limit).offset(offset).all()
    ]
    popular_threads = [
        sub.as_dict() for sub in Subthread.query.order_by(Subthread.post_count.desc()).limit(limit).offset(offset).all()
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
    subthread_list = [sub.as_dict() for sub in Subthread.query.filter(Subthread.name.ilike(thread_name)).all()]
    return jsonify(subthread_list), 200


@threads.route("/threads/get/all")
def get_all_thread():
    threads = Subthread.query.order_by(Subthread.name).all()
    return jsonify([t.as_dict() for t in threads]), 200


@threads.route("/threads/<thread_name>")
def get_thread_by_name(thread_name):
    subthread = Subthread.query.filter_by(name=f"t/{thread_name}").first()
    if not subthread:
        return jsonify({"message": "Thread not found"}), 404
    return (
        jsonify({"threadData": subthread.as_dict(current_user.id if current_user.is_authenticated else None)}),
        200,
    )


@threads.route("threads/subscription/<tid>", methods=["POST"])
@login_required
def new_subscription(tid):
    subthread = Subthread.query.filter_by(id=tid).first()
    subscription = Subscription.query.filter_by(user_id=current_user.id, subthread_id=tid).first()
    if subscription or not subthread:
        return jsonify({"message": "Invalid Subscription"}), 400
    Subscription.add(tid, current_user.id, subthread)
    return jsonify({"message": "Subscribed"}), 200


@threads.route("threads/subscription/<tid>", methods=["DELETE"])
@login_required
def del_subscription(tid):
    subscription = Subscription.query.filter_by(user_id=current_user.id, subthread_id=tid).first()
    if subscription:
        subscription.remove()
    else:
        return jsonify({"message": "Invalid Subscription"}), 400
    return jsonify({"message": "UnSubscribed"}), 200


@threads.route("/thread", methods=["POST"])
@login_required
def new_thread():
    image = request.files.get("media")
    form_data = request.form.to_dict()
    if not form_data.get("name", "").strip():
        return jsonify({"message": "Thread name is required"}), 400
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
    return (
        jsonify(
            {
                "message": "Thread updated",
                "new_data": {"threadData": thread.as_dict(current_user.id if current_user.is_authenticated else None)},
            }
        ),
        200,
    )


@threads.route("/thread/mod/<tid>/<username>", methods=["PUT"])
@login_required
@auth_role(["admin", "mod"])
def new_mod(tid, username):
    user = User.query.filter_by(username=username).first()
    if user:
        UserRole.add_moderator(user.id, tid)
        return jsonify({"message": "Moderator added"}), 200
    return jsonify({"message": "Invalid User"}), 400


@threads.route("/thread/mod/<tid>/<username>", methods=["DELETE"])
@login_required
@auth_role(["admin", "mod"])
def delete_mod(tid, username):
    user = User.query.filter_by(username=username).first()
    thread = Subthread.query.filter_by(id=tid).first()
    if user and thread:
        if thread.created_by == user.id and not current_user.has_role("admin"):
            return jsonify({"message": "Cannot Remove Thread Creator"}), 400
        UserRole.query.filter_by(user_id=user.id, subthread_id=tid).delete()
        db.session.commit()
        return jsonify({"message": "Moderator deleted"}), 200
    return jsonify({"message": "Invalid User"}), 400
