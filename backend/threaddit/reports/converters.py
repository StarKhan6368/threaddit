from typing import override

import sqlalchemy as sa
from flask import abort
from werkzeug.routing import BaseConverter

from threaddit import db
from threaddit.reports.models import Reports, ReportType


class ReportConverter(BaseConverter):
    regex = r"[0-9]+"

    @override
    def to_python(self, value: str) -> "Reports":
        report = db.session.scalar(sa.select(Reports).where(Reports.id == value))
        if not report:
            abort(404, {"report_id": f"Report with ID {value} not found"})
        return report

    @override
    def to_url(self, value: str | int) -> str:
        return str(value)


class ReportTypeConverter(BaseConverter):
    regex = r"[0-9]+"

    @override
    def to_python(self, value: str) -> "ReportType":
        report_type = db.session.scalar(sa.select(ReportType).where(ReportType.id == value))
        if not report_type:
            abort(404, {"report_type_id": f"Report Type with ID {value} not found"})
        return report_type

    @override
    def to_url(self, value: str | int) -> str:
        return str(value)
