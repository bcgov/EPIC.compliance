"""Test ceb_summary report service."""
from datetime import datetime, timedelta
from faker import Faker
import pytest

from compliance_api.models.complaint.complaint import Complaint, ComplaintStatusEnum
from compliance_api.models.complaint.complaint_enum import ComplaintSourceEnum
from compliance_api.models.complaint.complaint_option import ComplaintSource
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


@pytest.fixture(autouse=True)
def before_and_after_each():
    """Fixture to execute before and after each test."""
    _create_test_inspection_requirement()
    _create_test_complaint()
    yield
    _clean_up_database()


def test_build_inspections_tab_query_no_date_range():
    """Test building inspections tab query with no date range."""
    generator = ceb_summary.CEBSummaryReportGenerator({})
    results = generator._build_inspections_tab_query().all()
    insp_req = db.session.query(InspectionRequirement).first()
    assert len(results) == 1
    assert results[0].InspectionRequirement == insp_req


def test_build_inspections_tab_query_results_expected_within_date_range():
    """Test building inspections tab query with date range that includes data."""
    generator = ceb_summary.CEBSummaryReportGenerator({
        "start_date": datetime.now() - timedelta(days=1),
        "end_date": datetime.now() + timedelta(days=1)
    })
    results = generator._build_inspections_tab_query().all()
    insp_req = db.session.query(InspectionRequirement).first()
    assert len(results) == 1
    assert results[0].InspectionRequirement == insp_req


def test_build_inspections_tab_query_no_results_expected_with_start_date():
    """Test building inspections tab query with start date that excludes data."""
    generator = ceb_summary.CEBSummaryReportGenerator({
        "start_date": datetime.now() + timedelta(days=10)
    })
    results = generator._build_inspections_tab_query().all()
    assert len(results) == 0


def test_build_inspections_tab_query_no_results_expected_with_end_date():
    """Test building inspections tab query with end date that excludes data."""
    generator = ceb_summary.CEBSummaryReportGenerator({"end_date": datetime.now() - timedelta(days=10)})
    results = generator._build_inspections_tab_query().all()
    assert len(results) == 0


def test_build_complaints_tab_query_no_date_range():
    """Test building complaints tab query with no date range."""
    generator = ceb_summary.CEBSummaryReportGenerator({})
    results = generator._build_complaints_tab_query().all()
    complaint = db.session.query(Complaint).first()
    assert len(results) == 1
    assert results[0].complaint_number == complaint.complaint_number


def test_build_complaints_tab_query_results_expected_within_date_range():
    """Test building complaints tab query with date range that includes data."""
    generator = ceb_summary.CEBSummaryReportGenerator({
        "start_date": datetime.now() - timedelta(days=1),
        "end_date": datetime.now() + timedelta(days=1)
    })
    results = generator._build_complaints_tab_query().all()
    complaint = db.session.query(Complaint).first()
    assert len(results) == 1
    assert results[0].complaint_number == complaint.complaint_number


def test_build_complaints_tab_query_no_results_expected_with_start_date():
    """Test building complaints tab query with start date that excludes data."""
    generator = ceb_summary.CEBSummaryReportGenerator({
        "start_date": datetime.now() + timedelta(days=10)
    })
    results = generator._build_complaints_tab_query().all()
    assert len(results) == 0


def test_build_complaints_tab_query_no_results_expected_with_end_date():
    """Test building complaints tab query with end date that excludes data."""
    generator = ceb_summary.CEBSummaryReportGenerator({"end_date": datetime.now() - timedelta(days=10)})
    results = generator._build_complaints_tab_query().all()
    assert len(results) == 0


def _create_test_inspection_requirement():
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
        start_date=datetime.now(),
        end_date=datetime.now() + timedelta(days=1),
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


def _create_test_complaint():
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

    complaint_source = ComplaintSource(
        name=ComplaintSourceEnum.PUBLIC.value
    )

    db.session.add_all([topic, complaint_source])
    db.session.flush()

    complaint = Complaint(
        case_file_id=case_file.id,
        date_received=datetime.now(),
        source_type_id=complaint_source.id,
        concern_description=fake.text(max_nb_chars=200),
        status=ComplaintStatusEnum.OPEN,
        complaint_number=fake.pystr(min_chars=5, max_chars=10)
    )

    db.session.add(complaint)
    db.session.commit()


def _clean_up_database():
    """Clean up the database after tests."""
    db.session.query(InspectionReqEnforcementMap).delete()
    db.session.query(InspectionRequirement).delete()
    db.session.query(InspectionRecord).delete()
    db.session.query(Inspection).delete()
    db.session.query(StaffUser).delete()
    db.session.query(ComplianceFindingOption).delete()
    db.session.query(Topic).delete()
    db.session.query(Complaint).delete()
    db.session.query(CaseFile).delete()
    db.session.query(ComplaintSource).delete()
    db.session.commit()
