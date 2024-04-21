import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.auth.decorators import admin_mod, admin_mod_author
from threaddit.moderations.models import UserRole
from threaddit.threads.models import Subscription, Thread
from threaddit.threads.schemas import (
    FlairsType,
    PaginationSchema,
    PaginationType,
    ThreadBarSchema,
    ThreadFlairsSchema,
    ThreadFormSchema,
    ThreadFormType,
    ThreadLinkSchema,
    ThreadSchema,
)

threads = Blueprint("threads", __name__, url_prefix="/threads")
thread_schema = ThreadSchema()
thread_add_schema = ThreadFormSchema()
thread_patch_schema = ThreadFormSchema(exclude=("name",))
threads_link_schema = ThreadLinkSchema(many=True)
threads_bar_schema = ThreadBarSchema()
paginate_schema = PaginationSchema()
thread_flairs_schema = ThreadFlairsSchema()


@threads.route("/", methods=["GET"])
@jwt_required(optional=True)
def threads_get():
    query: "PaginationType" = paginate_schema.load(request.args)
    limit = query["limit"]
    page = query["page"]

    all_threads = db.paginate(
        sa.select(Thread).order_by(Thread.subscriber_count.desc()), page=page, per_page=limit, error_out=False
    )

    subscribed_threads = db.paginate(
        sa.select(Thread).join(Subscription).where(Subscription.user_id == current_user.id),
        page=page,
        per_page=limit,
        error_out=False,
    )

    popular_threads = db.paginate(
        sa.select(Thread).order_by(Thread.subscriber_count.desc()), page=page, per_page=limit, error_out=False
    )

    return jsonify(
        threads={
            "subscribed": threads_bar_schema.dump(subscribed_threads),
            "all": threads_bar_schema.dump(all_threads),
            "popular": threads_bar_schema.dump(popular_threads),
        },
    ), 200


@threads.route("/", methods=["POST"])
@jwt_required()
def thread_add():
    form: "ThreadFormType" = thread_add_schema.load(request.form | request.files)
    thread = db.session.scalar(sa.select(Thread).where(Thread.name == form["name"]))
    if thread:
        return abort(400, {"name": f"Thread with name {form.get("name")} already exists"})
    thread = Thread.add(form, current_user)
    UserRole.add_moderator(current_user, current_user, thread)
    db.session.commit()
    return thread_schema.dump(thread), 200


@threads.route("/<thread_id:thread>", methods=["GET"])
@jwt_required(optional=True)
def thread_get(thread: "Thread"):
    return thread_schema.dump(thread), 200


@threads.route("/<thread_id:thread>", methods=["PATCH"])
@jwt_required()
@admin_mod_author()
def thread_update(thread: "Thread"):
    form: "ThreadFormType" = thread_patch_schema.load(request.form | request.files)
    thread.update(form)
    db.session.commit()
    return thread_schema.dump(thread), 200


@threads.route("/search/<thread_name>", methods=["GET"])
@jwt_required(optional=True)
def thread_search(thread_name: str):
    return threads_link_schema.dump(
        db.session.scalars(sa.select(Thread).where(Thread.name.ilike(f"%{thread_name}%"))).all()
    ), 200


@threads.route("/<thread_id:thread>/flairs", methods=["POST"])
@jwt_required()
@admin_mod()
def thread_flairs_add(thread: "Thread"):
    body: "FlairsType" = thread_flairs_schema.load(request.json)
    thread.flairs = list(set(thread.flairs).union(body["flairs"]))
    db.session.commit()
    return thread_schema.dump(thread), 200


@threads.route("/<thread_id:thread>/flairs", methods=["DELETE"])
@jwt_required()
@admin_mod()
def thread_flairs_del(thread: "Thread"):
    body: "FlairsType" = thread_flairs_schema.load(request.json)
    thread.flairs = list(set(thread.flairs).difference(body["flairs"]))
    db.session.commit()
    return thread_schema.dump(thread), 200


@threads.route("/<thread_id:thread>/subscription", methods=["POST"])
@jwt_required()
def subscription_add(thread: "Thread"):
    if db.session.scalar(
        sa.select(Subscription).where(Subscription.user_id == current_user.id, Subscription.thread_id == thread.id)
    ):
        return abort(400, {"message": "Subscription already exists"})
    Subscription.add(current_user, thread)
    db.session.commit()
    return jsonify(message="Subscribed"), 200


@threads.route("/<thread_id:thread>/subscription", methods=["DELETE"])
@jwt_required()
def subscription_del(thread: "Thread"):
    subscription = db.session.scalar(
        sa.select(Subscription).where(Subscription.user_id == current_user.id, Subscription.thread_id == thread.id)
    )
    if not subscription:
        return abort(400, {"message": "Subscription does not exist"})
    subscription.delete(thread)
    db.session.commit()
    return jsonify(message="UnSubscribed"), 200
