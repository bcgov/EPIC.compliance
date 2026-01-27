"""Service for report."""

from compliance_api.models.report_enum import ReportTypeEnum
from .ceb_summary import CEBSummaryReportGenerator


class ReportService:
    """Report service."""

    _generator_map = {
        ReportTypeEnum.CEB_SUMMARY: CEBSummaryReportGenerator,
    }

    @classmethod
    def generate_report(cls, report_data, report_type):
        """Generate report."""
        generator_class = ReportService._generator_map.get(report_type)

        if not generator_class:
            raise ValueError(f"Unknown report type: {report_type}")
        generator = generator_class(report_data)
        return generator.generate()
