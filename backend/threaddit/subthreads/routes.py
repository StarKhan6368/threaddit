from threaddit.subthreads.models import Subthread, Subscription
from flask_login import current_user
from flask import Blueprint, jsonify, request

subthread = Blueprint("subthread", __name__, url_prefix="/api")


@subthread.route("/subthreads/all", methods=["GET"])
def get_subthreads():
    limit = request.args.get("limit", default=10, type=int)
    offset = request.args.get("offset", default=0, type=int)
    subscribed_threads = []
    if current_user.is_authenticated:
        pass
        # subscribed_threads = [thread.as_dict() for thread in Subscription.query.filter_by(user_id=current_user.id)
        #                       .limit(limit).offset(offset).all()]
    all_threads = [thread.as_dict() for thread in Subthread.query.limit(limit).offset(offset).all()]
    popular_threads = [thread.as_dict() for thread in Subthread.query.limit(limit).offset(offset).all()]
    return jsonify({"subscribed": subscribed_threads, "all": all_threads, "popular": popular_threads}), 200
