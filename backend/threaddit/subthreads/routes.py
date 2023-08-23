from threaddit.subthreads.models import Subthread, SubthreadInfo
from flask_login import current_user
from flask import Blueprint, jsonify, request

threads = Blueprint("threads", __name__, url_prefix="/api")


@threads.route("/threads/all", methods=["GET"])
def get_subthreads():
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)
    subscribed_threads = []
    if current_user.is_authenticated:
        pass
        # subscribed_threads = [thread.as_dict() for thread in
        # Subscription.query.filter_by(user_id=current_user.id)
        # .limit(limit).offset(offset).all()]
    all_threads = [
        thread.as_dict() for thread in Subthread.query.limit(limit).offset(offset).all()
    ]
    popular_threads = [
        thread.as_dict() for thread in Subthread.query.limit(limit).offset(offset).all()
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
            SubthreadInfo.name.like(thread_name)
        ).all()
    ]
    return jsonify(subthread_list), 200
