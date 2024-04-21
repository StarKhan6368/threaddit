from typing import TypedDict

import sqlalchemy as sa
from flask import abort
from marshmallow import fields, post_load

from threaddit import db, ma
from threaddit.moderations.models import ModAdminInv, UserRole
from threaddit.reports.models import ReportType
from threaddit.threads.schemas import ThreadLinkSchema
from threaddit.users.schemas import UserLinkSchema


class ResLockType(TypedDict):
    mod_comment: str | None
    report_type_id: "ReportType"
    thread_id: int


class ResLockSchema(ma.Schema):
    mod_comment = fields.String(required=False, load_default=None)
    report_type_id = fields.Integer(required=True)
    thread_id = fields.Integer(required=True)

    # noinspection PyUnusedLocal
    @post_load
    def check_report_type_id(self, data, **kwargs):  # noqa: ARG002
        report_type = db.session.scalar(sa.select(ReportType).where(ReportType.id == data["report_type_id"]))
        if not report_type:
            abort(404, {"report_type_id": f"Report Type with ID {data['report_type_id']} not found"})
        if report_type.thread_id != data["thread_id"]:
            abort(404, {"report_type_id": f"Report Type with ID {data['report_type_id']} not found in thread"})
        return data


class UserRoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserRole
        exclude = ("id", "grantee_id", "granter_id", "thread_id")

    role_type = fields.Function(lambda obj: obj.role_type.name, dump_only=True)
    granter = fields.Nested(UserLinkSchema())
    grantee = fields.Nested(UserLinkSchema())
    thread = fields.Nested(ThreadLinkSchema())


class ModAdminInvSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ModAdminInv
        exclude = ("id", "grantee_id", "granter_id", "thread_id")

    role_type = fields.Function(lambda obj: obj.role_type.name, dump_only=True)
    status = fields.Function(lambda obj: obj.status.name, dump_only=True)
    granter = fields.Nested(UserLinkSchema())
    grantee = fields.Nested(UserLinkSchema())
    thread = fields.Nested(ThreadLinkSchema())
