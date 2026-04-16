"""Test ceb_summary report service."""
from datetime import datetime, timedelta
from faker import Faker
import pytest

from compliance_api.models import db
from compliance_api.models.case_file import CaseFile
from compliance_api.models.inspection.inspection_req_enforcement_map import InspectionReqEnforcementMap
from compliance_api.models.inspection_record import InspectionRecord
from compliance_api.services.report import ceb_summary
from compliance_api.models.inspection.inspection import Inspection
from compliance_api.models.inspection.inspection_requirement import InspectionRequirement
from compliance_api.models.topic import Topic
from compliance_api.models.compliance_finding import ComplianceFindingOption
from compliance_api.models.staff_user import StaffUser

fake = Faker()


class TestCEBSummaryReportGenerator:
    """Test CEB Summary Report Generator."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Fixture to execute before and after each test."""
        self.insp_req = self._create_test_inspection_requirement()
        yield
        self._clean_up_database()

    def test_build_inspections_tab_query(self):
        """Test building inspections tab query with no date range."""
        generator = ceb_summary.CEBSummaryReportGenerator({
            "start_date": datetime.now() + timedelta(days=100),
        })
        results = generator._build_inspections_tab_query().all()
        assert len(results) == 1
        assert results[0].InspectionRequirement == self.insp_req

    def test_build_inspections_tab_query_results_expected_within_date_range(self):
        """Test building inspections tab query with date range that includes data."""
        generator = ceb_summary.CEBSummaryReportGenerator({
            "start_date": datetime.now() + timedelta(days=150),
            "end_date": datetime.now() + timedelta(days=153)
        })
        results = generator._build_inspections_tab_query().all()
        assert results[0].InspectionRequirement == self.insp_req

    def test_build_inspections_tab_query_no_results_expected_with_start_date(self):
        """Test building inspections tab query with start date that excludes data."""
        generator = ceb_summary.CEBSummaryReportGenerator({
            "start_date": datetime.now() + timedelta(days=154)
        })
        results = generator._build_inspections_tab_query().all()
        assert len(results) == 0

    def test_build_inspections_tab_query_no_results_expected_with_end_date(self):
        """Test building inspections tab query with end date that excludes data."""
        generator = ceb_summary.CEBSummaryReportGenerator({"end_date": datetime.now() - timedelta(days=10)})
        results = generator._build_inspections_tab_query().all()
        assert len(results) == 0

    def _create_test_inspection_requirement(self):
        """Create an inspection requirement for testing."""
        case_file = CaseFile(
            date_created=datetime.now(),
            case_file_number=fake.pystr(min_chars=5, max_chars=10),
            initiation_id=1
        )

        db.session.add(case_file)
        db.session.flush()

        topic = Topic(
            name="Test Topic"
        )
        finding = ComplianceFindingOption(
            name=fake.pystr(min_chars=5, max_chars=10)
        )
        officer = StaffUser(
            first_name=fake.pystr(min_chars=5, max_chars=10),
            last_name=fake.last_name(),
            position_id=1
        )
        inspection = Inspection(
            ir_number=fake.pystr(min_chars=5, max_chars=10),
            primary_officer=officer,
            start_date=datetime.now() + timedelta(days=152),
            end_date=datetime.now() + timedelta(days=152),
            initiation_id=1,
            case_file_id=case_file.id
        )

        db.session.add_all([topic, finding, officer, inspection, case_file])
        db.session.flush()

        inspection_record = InspectionRecord(
            inspection_id=inspection.id,
            date_issued=datetime.now(),
            ir_status_id=1
        )

        db.session.add(inspection_record)
        db.session.flush()

        insp_req = InspectionRequirement(
            inspection_id=inspection.id,
            topic_id=topic.id,
            compliance_finding_id=finding.id,
            summary="Requirement 1",
            sort_order=1,
        )

        db.session.add(insp_req)
        db.session.flush()

        insp_req_enf_map = InspectionReqEnforcementMap(
            requirement_id=insp_req.id,
            enforcement_action_id=1
        )

        db.session.add(insp_req_enf_map)
        db.session.commit()

        return insp_req

    def _clean_up_database(self):
        """Clean up the database after tests."""
        db.session.query(InspectionReqEnforcementMap).where(
            InspectionReqEnforcementMap.requirement_id == self.insp_req.id
        ).delete()
        db.session.query(InspectionRequirement).where(InspectionRequirement.id == self.insp_req.id).delete()
        db.session.commit()
