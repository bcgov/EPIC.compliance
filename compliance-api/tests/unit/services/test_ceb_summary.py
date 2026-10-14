"""Test ceb_summary report service."""
from datetime import datetime, timedelta
from faker import Faker
import pytest

from compliance_api.models import db
from compliance_api.models.case_file import CaseFile
from compliance_api.models.complaint.complaint import Complaint, ComplaintStatusEnum
from compliance_api.models.complaint.complaint_option import ComplaintSource, ComplaintSourceEnum
from compliance_api.models.inspection.inspection_req_enforcement_map import InspectionReqEnforcementMap
from compliance_api.models.inspection.inspection_attendance import InspectionAttendance
from compliance_api.models.inspection.inspection_firstnation import InspectionFirstnation
from compliance_api.models.inspection.inspection_option import InspectionAttendanceOption
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
        self.complaints = []
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

    def test_build_complaints_tab_query_includes_complaint_received_within_date_range(self):
        """Test complaints tab query includes complaints received within the date range."""
        complaint = self._create_test_complaint(datetime.now() + timedelta(days=152))
        generator = ceb_summary.CEBSummaryReportGenerator({
            "start_date": datetime.now() + timedelta(days=150),
            "end_date": datetime.now() + timedelta(days=153)
        })
        results = generator._build_complaints_tab_query().all()
        assert complaint.complaint_number in [row.complaint_number for row in results]

    def test_build_complaints_tab_query_excludes_complaint_received_before_start_date(self):
        """Test complaints tab query excludes complaints received before the start date."""
        complaint = self._create_test_complaint(datetime.now() + timedelta(days=149))
        generator = ceb_summary.CEBSummaryReportGenerator({
            "start_date": datetime.now() + timedelta(days=150),
            "end_date": datetime.now() + timedelta(days=153)
        })
        results = generator._build_complaints_tab_query().all()
        assert complaint.complaint_number not in [row.complaint_number for row in results]

    def test_build_complaints_tab_query_excludes_complaint_received_after_end_date(self):
        """Test complaints tab query excludes complaints received after the end date."""
        complaint = self._create_test_complaint(datetime.now() + timedelta(days=154))
        generator = ceb_summary.CEBSummaryReportGenerator({
            "start_date": datetime.now() + timedelta(days=150),
            "end_date": datetime.now() + timedelta(days=153)
        })
        results = generator._build_complaints_tab_query().all()
        assert complaint.complaint_number not in [row.complaint_number for row in results]

    def _create_test_complaint(self, date_received):
        """Create a complaint received on the given date."""
        case_file = CaseFile(
            date_created=datetime.now(),
            case_file_number=fake.pystr(min_chars=5, max_chars=10),
            initiation_id=1
        )
        db.session.add(case_file)
        db.session.flush()

        complaint_source = db.session.query(ComplaintSource).filter(
            ComplaintSource.name == ComplaintSourceEnum.PUBLIC.value
        ).first()
        if not complaint_source:
            complaint_source = ComplaintSource(name=ComplaintSourceEnum.PUBLIC.value)
            db.session.add(complaint_source)
            db.session.flush()

        complaint = Complaint(
            case_file_id=case_file.id,
            date_received=date_received,
            source_type_id=complaint_source.id,
            concern_description=fake.text(max_nb_chars=200),
            status=ComplaintStatusEnum.OPEN,
            complaint_number=fake.pystr(min_chars=5, max_chars=10),
        )
        db.session.add(complaint)
        db.session.commit()
        self.complaints.append(complaint)

        return complaint

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

        # Get existing attendance option (seeded data) for INNER JOIN in query
        attendance_option = db.session.query(InspectionAttendanceOption).first()

        inspection_attendance = InspectionAttendance(
            inspection_id=inspection.id,
            attendance_option_id=attendance_option.id
        )
        inspection_firstnation = InspectionFirstnation(
            inspection_id=inspection.id,
            firstnation_id=1
        )
        db.session.add_all([inspection_attendance, inspection_firstnation])
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
        db.session.query(Complaint).where(Complaint.id.in_([c.id for c in self.complaints])).delete()
        db.session.commit()
