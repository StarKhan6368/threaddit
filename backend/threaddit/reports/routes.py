from typing import TYPE_CHECKING

import sqlalchemy as sa
from flask import Blueprint, abort, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from threaddit import db
from threaddit.auth.decorators import admin_mod
from threaddit.reports.models import Reports, ReportType
from threaddit.reports.schemas import (
    NewReportSchema,
    NewReportType,
    ReportResolveSchema,
    ReportResolveType,
    ReportSchema,
    ReportTypeAdd,
    ReportTypeAddSchema,
    ReportTypeSchema,
)

if TYPE_CHECKING:
    from threaddit.comments.models import Comments
    from threaddit.posts.models import Posts
    from threaddit.threads.models import Thread
    from threaddit.users.models import User

reports = Blueprint("reports", __name__)
new_report_schema = NewReportSchema()
report_resolve_schema = ReportResolveSchema()
report_schema = ReportSchema()
reports_schema = ReportSchema(many=True)
report_types_schema = ReportTypeSchema(many=True)
new_report_type_schema = ReportTypeAddSchema(many=True)


@reports.route("/threads/<thread_id:thread>/posts/<post_id:post>/reports", methods=["POST"])
@jwt_required()
def post_report_add(thread: "Thread", post: "Posts"):
    report = Reports.get_report(current_user, thread, post)
    if report:
        abort(400, {"message": "You have already reported this post"})
    body: "NewReportType" = new_report_schema.load(request.json | {"thread_id": thread.id})
    report = Reports.add(current_user, thread, post, body)
    db.session.commit()
    return report_schema.dump(report), 200


@reports.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/reports", methods=["POST"]
)
@jwt_required()
def comment_report_add(thread: "Thread", post: "Posts", comment: "Comments"):
    report = Reports.get_report(current_user, thread, post, comment)
    if report:
        abort(400, {"message": "You have already reported this comment"})
    body: "NewReportType" = new_report_schema.load(request.json)
    report = Reports.add(current_user, thread, post, body, comment=comment)
    db.session.commit()
    return report_schema.dump(report), 200


@reports.route("/threads/<thread_id:thread>/posts/<post_id:post>/reports", methods=["GET"])
@jwt_required()
@admin_mod()
def post_reports_get(thread: "Thread", post: "Posts"):
    post.validate_post(thread)
    reports_list = db.session.scalars(
        sa.select(Reports)
        .where(Reports.post_id == post.id, Reports.comment_id.is_(None))
        .order_by(Reports.created_at.desc())
    ).all()
    return reports_schema.dump(reports_list), 200


@reports.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/reports", methods=["GET"]
)
@jwt_required()
@admin_mod()
def comment_reports_get(thread: "Thread", post: "Posts", comment: "Comments"):
    comment.validate_comment(thread, post)
    reports_list = db.session.scalars(
        sa.select(Reports).where(Reports.comment_id == comment.id).order_by(Reports.created_at.desc())
    ).all()
    return reports_schema.dump(reports_list), 200


@reports.route("/users/<user_name:user>/reports", methods=["GET"])
@jwt_required()
@admin_mod()
def user_reports_get(user: "User"):
    reports_list = db.session.scalars(
        sa.select(Reports).where(Reports.reporter_id == user.id).order_by(Reports.created_at.desc())
    ).all()
    return reports_schema.dump(reports_list), 200


@reports.route("/me/reports", methods=["GET"])
@jwt_required()
def me_reports_get():
    reports_list = db.session.scalars(
        sa.select(Reports).where(Reports.reporter_id == current_user.id).order_by(Reports.created_at.desc())
    ).all()
    return reports_schema.dump(reports_list), 200


@reports.route("/threads/<thread_id:thread>/posts/<post_id:post>/reports/<report_id:report>/resolve", methods=["POST"])
@jwt_required()
@admin_mod()
def post_report_resolve(thread: "Thread", post: "Posts", report: "Reports"):
    post.validate_post(thread)
    body: "ReportResolveType" = report_resolve_schema.load(request.json)
    report.resolve(thread, post, body)
    db.session.commit()
    return report_schema.dump(report), 200


@reports.route(
    "/threads/<thread_id:thread>/posts/<post_id:post>/comments/<comment_id:comment>/reports/<report_id:report>/resolve",
    methods=["POST"],
)
@jwt_required()
@admin_mod()
def comment_report_resolve(thread: "Thread", post: "Posts", comment: "Comments", report: "Reports"):
    comment.validate_comment(thread, post)
    body: "ReportResolveType" = report_resolve_schema.load(request.json)
    report.resolve(thread, post, body, comment=comment)
    db.session.commit()
    return report_schema.dump(report), 200


@reports.route("/threads/<thread_id:thread>/reports", methods=["POST"])
@jwt_required()
@admin_mod()
def thread_report_type_add(thread: "Thread"):
    if not isinstance(request.json, list):
        return abort(400, {"message": "Invalid request body, should be list of report types"})
    body: list["ReportTypeAdd"] = new_report_type_schema.load(request.json)
    report_types = ReportType.add_types(thread, body)
    db.session.commit()
    return report_types_schema.dump(report_types), 200


@reports.route("/threads/<thread_id:thread>/reports", methods=["GET"])
@jwt_required()
def thread_report_types_get(thread: "Thread"):
    report_types = db.session.scalars(sa.select(ReportType).where(ReportType.thread_id == thread.id)).all()
    return report_types_schema.dump(report_types), 200


@reports.route("/threads/<thread_id:thread>/reports/<report_type_id:report_type>", methods=["DELETE"])
@jwt_required()
@admin_mod()
def thread_report_type_delete(thread: "Thread", report_type: "ReportType"):
    if report_type.thread_id != thread.id:
        return abort(400, {"message": f"Report type not found in thread {thread.name}"})
    report_type.delete()
    db.session.commit()
    return jsonify(message="Report Type Deleted"), 200
