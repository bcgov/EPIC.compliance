"""Service for report."""

from compliance_api.models.report_enum import ReportTypeEnum
from compliance_api.services.report.case_file_management import CaseFileManagementReportGenerator
from compliance_api.services.report.first_nation import FirstNationReportGenerator
from compliance_api.services.report.project_compliance import ProjectComplianceReportGenerator
from .ceb_summary import CEBSummaryReportGenerator


class ReportService:
    """Report service."""

    _generator_map = {
        ReportTypeEnum.CEB_SUMMARY: CEBSummaryReportGenerator,
        ReportTypeEnum.CASE_FILE_MANAGEMENT: CaseFileManagementReportGenerator,
        ReportTypeEnum.FIRST_NATION: FirstNationReportGenerator,
        ReportTypeEnum.PROJECT_COMPLIANCE: ProjectComplianceReportGenerator,
    }

    @classmethod
    def generate_report(cls, report_data, report_type):
        """Generate report."""
        generator_class = ReportService._generator_map.get(report_type)

        if not generator_class:
            raise ValueError(f"Unknown report type: {report_type}")
        generator = generator_class(report_data)
        return generator.generate(), generator
