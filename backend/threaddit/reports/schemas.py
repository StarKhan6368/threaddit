import re
from typing import TypedDict

import sqlalchemy as sa
from flask import abort
from marshmallow import ValidationError, fields, post_load, validate

from threaddit import db, ma
from threaddit.reports.models import ReportAction, Reports, ReportStatus, ReportType


class NewReportType(TypedDict):
    reporter_comment: str | None
    thread_id: int
    report_type: "ReportType"


class ReportResolveType(TypedDict):
    mod_comment: str | None
    resolution: "ReportStatus"
    action: "ReportAction"
    disable_reports: bool


class ReportTypeAdd(TypedDict):
    name: str
    description: str | None


class ReportTypeId(fields.Field):
    def _deserialize(
        self,
        value: int,
        attr: str | None,
        data: dict,  # noqa: ARG002
        **kwargs,  # noqa: ARG002
    ) -> "ReportType":
        try:
            value = int(value)
            if value < 1:
                raise ValidationError("Invalid Report Type ID", field_name=attr)
        except (TypeError, ValueError) as e:
            raise ValidationError("Invalid Report Type ID", field_name=attr) from e

        report_type = db.session.scalar(sa.select(ReportType).where(ReportType.id == value))
        if not report_type:
            error_msg = f"Invalid Report Type ID {value} doesn't exist"
            raise ValidationError(error_msg, field_name=attr)
        return report_type


class NewReportSchema(ma.Schema):
    thread_id = fields.Integer(required=True)
    report_type = ReportTypeId(required=True)
    reporter_comment = fields.String(
        required=False,
        validate=validate.Length(min=1, error="Report cannot be empty"),
        load_default=None,
        data_key="comment",
    )

    # noinspection PyUnusedLocal
    @post_load
    def validate_content(self, data: "NewReportType", **kwargs) -> "NewReportType":  # noqa: ARG002
        if data["reporter_comment"] and re.match(r"^\s*$", data["reporter_comment"]):
            raise ValidationError("Report Comment cannot be empty", field_name="reporter_comment")

        if data["report_type"].thread_id != data["thread_id"]:
            error = f"Report with ID {data['report_type'].id} Not Found in thread {data["thread_id"]}"
            raise ValidationError(error, field_name="report_type")

        return data


class ReportResolveSchema(ma.Schema):
    mod_comment = fields.String(
        validate=validate.Length(min=1, error="Comment cannot be empty"), required=False, load_default=None
    )
    resolution = fields.String(validate=validate.OneOf(["RESOLVED", "REJECTED"]), required=True)
    action = fields.String(validate=validate.OneOf([action.value for action in ReportAction]), required=True)
    disable_reports = fields.Boolean(required=False, load_default=False)

    # noinspection PyUnusedLocal
    @post_load
    def resolve_resolution(self, data, **kwargs) -> "ReportResolveType":  # noqa: ARG002
        data["resolution"] = ReportStatus[data["resolution"]]
        data["action"] = ReportAction[data["action"]]
        if data["resolution"] == ReportStatus.REJECTED and data["action"] != ReportAction.SKIPPED:
            raise ValidationError("Cannot lock or remove reports with status REJECTED", field_name="resolution")
        if data["resolution"] == ReportStatus.RESOLVED and data["action"] == ReportAction.SKIPPED:
            raise ValidationError("Cannot skip reports with status RESOLVED", field_name="resolution")
        return data


class ReportTypeAddSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1, error="Name cannot be empty"))
    description = fields.String(required=False, validate=validate.Length(min=1, max=100))

    # noinspection PyUnusedLocal
    @post_load
    def validate(self, data: "ReportTypeAdd", **kwargs) -> "ReportTypeAdd":  # noqa: ARG002
        if re.match(r"^\s*$", data["name"]):
            raise ValidationError("Name cannot be empty", field_name="name")

        if data["description"] and re.match(r"^\s*$", data["description"]):
            raise ValidationError("Description cannot be empty", field_name="description")

        return data


class ResReportTypeSchema(ma.Schema):
    report_id = fields.Integer(validate=validate.Range(min=1, error="Report type ID cannot be less than 1"))

    # noinspection PyUnusedLocal
    @post_load
    def check_id(self, data, **kwargs):  # noqa: ARG002
        report_type = db.session.scalar(sa.select(ReportType).where(ReportType.id == data["report_id"]))
        if not report_type:
            abort(404, {"report_id": f"Report Type with ID {data['report_id']} not found"})
        return data


class ReportTypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ReportType


class ReportSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Reports

    status = fields.Function(lambda obj: obj.status.value, deserialize=lambda v: ReportStatus(v))
    action = fields.Function(
        lambda obj: obj.action.value if obj.action else None, deserialize=lambda v: ReportAction(v)
    )
    report_type = fields.Nested(ReportTypeSchema())
