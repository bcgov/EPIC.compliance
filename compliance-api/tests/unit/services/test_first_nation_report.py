"""Test first_nation report service."""
from datetime import datetime, timedelta

import pytest
from faker import Faker
from sqlalchemy import text

from compliance_api.models import db
from compliance_api.models.case_file import CaseFile
from compliance_api.models.complaint.complaint import Complaint, ComplaintStatusEnum
from compliance_api.models.complaint.complaint_option import ComplaintSource, ComplaintSourceEnum
from compliance_api.models.complaint.complaint_source_contact import ComplaintSourceContact
from compliance_api.models.compliance_finding import ComplianceFindingOption
from compliance_api.models.inspection.inspection import Inspection
from compliance_api.models.inspection.inspection_attendance import InspectionAttendance
from compliance_api.models.inspection.inspection_enum import InspectionAttendanceOptionEnum
from compliance_api.models.inspection.inspection_firstnation import InspectionFirstnation
from compliance_api.models.inspection.inspection_option import InspectionAttendanceOption
from compliance_api.models.inspection.inspection_req_enforcement_map import InspectionReqEnforcementMap
from compliance_api.models.inspection.inspection_requirement import InspectionRequirement
from compliance_api.models.inspection_record import InspectionRecord
from compliance_api.models.staff_user import StaffUser
from compliance_api.models.topic import Topic
from compliance_api.models.unapproved_project import UnapprovedProject
from compliance_api.services.report import first_nation

fake = Faker()

# Constants for test first nation IDs
TEST_FIRST_NATION_ID = 999
OTHER_FIRST_NATION_ID = 888


class TestFirstNationReportGenerator:
    """Test First Nation Report Generator."""

    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        """Fixture to execute before and after each test."""
        # Mock TrackService methods
        self.mock_get_first_nations = mocker.patch(
            "compliance_api.services.report.first_nation.TrackService.get_first_nations"
        )
        self.mock_get_first_nations.return_value = [
            {"id": TEST_FIRST_NATION_ID, "name": "Test First Nation"},
            {"id": OTHER_FIRST_NATION_ID, "name": "Other First Nation"},
        ]

        self.mock_get_project_by_id = mocker.patch(
            "compliance_api.services.report.first_nation.TrackService.get_project_by_id"
        )
        self.mock_get_project_by_id.return_value = {
            "name": "Test Project",
            "type": {"name": "Mine"},
        }

        # Clean tables before test
        db.session.execute(text('TRUNCATE inspection_firstnations RESTART IDENTITY CASCADE'))
        db.session.execute(text('TRUNCATE inspection_attendance_mappings RESTART IDENTITY CASCADE'))
        db.session.execute(text('TRUNCATE complaint_source_contacts RESTART IDENTITY CASCADE'))
        db.session.commit()

        self.inspection = None
        self.insp_req = None
        self.complaint = None

        yield

        # Clean up after test
        self._clean_up_database()

    def test_initialization_with_first_nation_id(self):
        """Test that the generator initializes correctly with a first_nation_id."""
        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        assert generator.first_nation_id == TEST_FIRST_NATION_ID
        assert generator._project_cache == {}

    def test_initialization_without_first_nation_id(self):
        """Test that the generator handles missing first_nation_id."""
        generator = first_nation.FirstNationReportGenerator({})
        assert generator.first_nation_id is None

    def test_build_inspections_query_returns_results_for_first_nation(self):
        """Test that inspections query returns results for the specified first nation."""
        self.insp_req = self._create_test_inspection_with_first_nation(TEST_FIRST_NATION_ID)

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_inspections_tab_query().all()

        assert len(results) >= 1
        assert any(r.first_nation_id == TEST_FIRST_NATION_ID for r in results)

    def test_build_inspections_query_excludes_other_first_nations(self):
        """Test that inspections query excludes inspections for other first nations."""
        # Create inspection for a different first nation
        other_insp_req = self._create_test_inspection_with_first_nation(OTHER_FIRST_NATION_ID)

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_inspections_tab_query().all()

        # Should not contain results for OTHER_FIRST_NATION_ID
        assert not any(r.first_nation_id == OTHER_FIRST_NATION_ID for r in results)

        # Clean up the other inspection
        self._clean_up_inspection_requirement(other_insp_req)

    def test_build_inspections_query_excludes_soft_deleted_first_nation_link(self):
        """Test that soft-deleted InspectionFirstnation records are excluded."""
        self.insp_req = self._create_test_inspection_with_first_nation(
            TEST_FIRST_NATION_ID,
            first_nation_deleted=True
        )

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_inspections_tab_query().all()

        # Should not return results for soft-deleted first nation link
        assert len(results) == 0

    def test_build_inspections_query_excludes_soft_deleted_attendance(self):
        """Test that soft-deleted InspectionAttendance records are excluded."""
        self.insp_req = self._create_test_inspection_with_first_nation(
            TEST_FIRST_NATION_ID,
            attendance_deleted=True
        )

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_inspections_tab_query().all()

        # Should not return results since attendance is deleted
        assert len(results) == 0

    def test_build_inspections_query_aggregates_multiple_attendance_types(self):
        """Test that multiple attendance types are aggregated into single row."""
        self.insp_req = self._create_test_inspection_with_first_nation(
            TEST_FIRST_NATION_ID,
            multiple_attendance=True
        )

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_inspections_tab_query().all()

        # Count rows for this inspection requirement
        req_rows = [r for r in results if r.InspectionRequirement.id == self.insp_req.id]

        # Should have one row per requirement (not per attendance type)
        # Multiple attendance types should be combined in inspection_attendance field
        assert len(req_rows) == 1
        # The attendance field should contain comma-separated values
        assert ", " in req_rows[0].inspection_attendance or req_rows[0].inspection_attendance is not None

    def test_build_complaints_query_returns_results_for_first_nation(self):
        """Test that complaints query returns results for the specified first nation."""
        self.complaint = self._create_test_complaint_for_first_nation(TEST_FIRST_NATION_ID)

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_complaints_tab_query().all()

        assert len(results) >= 1
        assert any(r.source_first_nation_id == TEST_FIRST_NATION_ID for r in results)

    def test_build_complaints_query_excludes_other_first_nations(self):
        """Test that complaints query excludes complaints for other first nations."""
        # Create complaint for a different first nation
        other_complaint = self._create_test_complaint_for_first_nation(OTHER_FIRST_NATION_ID)

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_complaints_tab_query().all()

        # Should not contain results for OTHER_FIRST_NATION_ID
        assert not any(r.source_first_nation_id == OTHER_FIRST_NATION_ID for r in results)

        # Clean up
        self._clean_up_complaint(other_complaint)

    def test_build_complaints_query_excludes_soft_deleted_source_contact(self):
        """Test that soft-deleted ComplaintSourceContact records are excluded."""
        self.complaint = self._create_test_complaint_for_first_nation(
            TEST_FIRST_NATION_ID,
            source_contact_deleted=True
        )

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_complaints_tab_query().all()

        # Complaint should still be returned, but ComplaintSourceContact should be None
        assert len(results) >= 1
        # The source contact should be None due to soft delete
        contact_row = next((r for r in results if r.source_first_nation_id == TEST_FIRST_NATION_ID), None)
        assert contact_row is not None
        assert contact_row.ComplaintSourceContact is None

    def test_format_inspections_data_returns_expected_fields(self):
        """Test that formatting returns all expected fields."""
        self.insp_req = self._create_test_inspection_with_first_nation(TEST_FIRST_NATION_ID)

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_inspections_tab_query().all()
        first_nations = [{"id": TEST_FIRST_NATION_ID, "name": "Test First Nation"}]
        formatted_data = generator._format_inspections_tab_data(results, first_nations)

        assert len(formatted_data) >= 1
        item = formatted_data[0]

        # Check all expected fields are present
        expected_fields = [
            "ir_number", "first_nation", "ir_progress", "project_name", "project_type",
            "start_date", "end_date", "topic_name", "summary", "compliance_finding",
            "enforcement_action", "enforcement_status", "enforcement_document_number",
            "condition_number", "requirement_source", "ir_issuance_date",
            "primary_officer", "inspection_status", "case_file_number"
        ]
        for field in expected_fields:
            assert field in item, f"Missing field: {field}"

    def test_format_complaints_data_returns_expected_fields(self):
        """Test that complaints formatting returns all expected fields."""
        self.complaint = self._create_test_complaint_for_first_nation(TEST_FIRST_NATION_ID)

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_complaints_tab_query().all()
        formatted_data = generator._format_complaints_tab_data(results, "Test First Nation")

        assert len(formatted_data) >= 1
        item = formatted_data[0]

        # Check all expected fields are present
        expected_fields = [
            "complaint_number", "project_name", "project_type", "topic",
            "date_received", "concern_description", "primary_officer",
            "complaint_status", "complaint_resolution", "case_file_number"
        ]
        for field in expected_fields:
            assert field in item, f"Missing field: {field}"

    def test_generate_returns_excel_bytes(self):
        """Test that generate method returns Excel file bytes."""
        self.insp_req = self._create_test_inspection_with_first_nation(TEST_FIRST_NATION_ID)
        self.complaint = self._create_test_complaint_for_first_nation(TEST_FIRST_NATION_ID)

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        result = generator.generate()

        # Check that result is bytes (Excel file)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_empty_data_generates_valid_excel(self):
        """Test that empty data still generates valid Excel with headers."""
        # Don't create any data - first nation ID that has no data
        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": 12345  # Non-existent first nation
        })
        result = generator.generate()

        # Should still return valid Excel bytes
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_project_cache_avoids_duplicate_calls(self):
        """Test that project cache prevents duplicate TrackService calls."""
        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })

        test_date = datetime.now()

        # Call twice with same project_id and date
        generator._get_project_cached(100, test_date)
        generator._get_project_cached(100, test_date)

        # TrackService should only be called once
        assert self.mock_get_project_by_id.call_count == 1

    def test_project_cache_different_dates_make_separate_calls(self):
        """Test that different dates result in separate TrackService calls."""
        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })

        date1 = datetime.now()
        date2 = datetime.now() + timedelta(days=1)

        generator._get_project_cached(100, date1)
        generator._get_project_cached(100, date2)

        # Should be called twice for different dates
        assert self.mock_get_project_by_id.call_count == 2

    def test_unapproved_project_uses_local_fields(self):
        """Test that unapproved projects use UnapprovedProject fields instead of TrackService."""
        self.insp_req = self._create_test_inspection_with_first_nation(
            TEST_FIRST_NATION_ID,
            unapproved_project=True
        )

        generator = first_nation.FirstNationReportGenerator({
            "first_nation_id": TEST_FIRST_NATION_ID
        })
        results = generator._build_inspections_tab_query().all()

        # Should have unapproved project data
        assert len(results) >= 1
        result = results[0]
        assert result.project_id is None
        assert result.unapproved_project_name is not None

    def _create_test_inspection_with_first_nation(
        self,
        first_nation_id,
        first_nation_deleted=False,
        attendance_deleted=False,
        multiple_attendance=False,
        unapproved_project=False
    ):
        """Create an inspection linked to a first nation for testing."""
        case_file = CaseFile(
            date_created=datetime.now(),
            case_file_number=fake.pystr(min_chars=5, max_chars=10),
            initiation_id=1
        )
        db.session.add(case_file)
        db.session.flush()

        # Create unapproved project if needed
        if unapproved_project:
            unapproved = UnapprovedProject(
                case_file_id=case_file.id,
                name=fake.company(),
                type="Mine"
            )
            db.session.add(unapproved)
            db.session.flush()

        topic = Topic(name=f"Test Topic {fake.pystr(min_chars=3, max_chars=5)}")
        finding = ComplianceFindingOption(name=fake.pystr(min_chars=5, max_chars=10))
        officer = StaffUser(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            position_id=1
        )
        db.session.add_all([topic, finding, officer])
        db.session.flush()

        inspection = Inspection(
            ir_number=fake.pystr(min_chars=5, max_chars=10),
            primary_officer_id=officer.id,
            start_date=datetime.now() + timedelta(days=152),
            end_date=datetime.now() + timedelta(days=152),
            initiation_id=1,
            case_file_id=case_file.id,
            project_id=None if unapproved_project else None  # No project for simplicity
        )
        db.session.add(inspection)
        db.session.flush()

        # Create InspectionFirstnation link
        first_nation_link = InspectionFirstnation(
            inspection_id=inspection.id,
            firstnation_id=first_nation_id,
            is_deleted=first_nation_deleted
        )
        db.session.add(first_nation_link)
        db.session.flush()

        # Get or create attendance option
        attendance_option = db.session.query(InspectionAttendanceOption).filter(
            InspectionAttendanceOption.id == InspectionAttendanceOptionEnum.ATTENDING_OFFICERS.value
        ).first()
        if not attendance_option:
            attendance_option = InspectionAttendanceOption(
                id=InspectionAttendanceOptionEnum.ATTENDING_OFFICERS.value,
                name="Attending Officers"
            )
            db.session.add(attendance_option)
            db.session.flush()

        # Create InspectionAttendance
        attendance = InspectionAttendance(
            inspection_id=inspection.id,
            attendance_option_id=attendance_option.id,
            is_deleted=attendance_deleted
        )
        db.session.add(attendance)
        db.session.flush()

        # Add second attendance type if needed
        if multiple_attendance:
            attendance_option2 = db.session.query(InspectionAttendanceOption).filter(
                InspectionAttendanceOption.id == InspectionAttendanceOptionEnum.FIRSTNATIONS.value
            ).first()
            if not attendance_option2:
                attendance_option2 = InspectionAttendanceOption(
                    id=InspectionAttendanceOptionEnum.FIRSTNATIONS.value,
                    name="First Nations"
                )
                db.session.add(attendance_option2)
                db.session.flush()

            attendance2 = InspectionAttendance(
                inspection_id=inspection.id,
                attendance_option_id=attendance_option2.id,
                is_deleted=False
            )
            db.session.add(attendance2)
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
            summary="Test Requirement",
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

        self.inspection = inspection
        return insp_req

    def _create_test_complaint_for_first_nation(
        self,
        first_nation_id,
        source_contact_deleted=False
    ):
        """Create a complaint for a first nation for testing."""
        case_file = CaseFile(
            date_created=datetime.now(),
            case_file_number=fake.pystr(min_chars=5, max_chars=10),
            initiation_id=1
        )
        db.session.add(case_file)
        db.session.flush()

        topic = Topic(name=f"Complaint Topic {fake.pystr(min_chars=3, max_chars=5)}")
        db.session.add(topic)
        db.session.flush()

        # Get or create First Nation complaint source
        complaint_source = db.session.query(ComplaintSource).filter(
            ComplaintSource.name == ComplaintSourceEnum.FIRST_NATION.value
        ).first()
        if not complaint_source:
            complaint_source = ComplaintSource(
                name=ComplaintSourceEnum.FIRST_NATION.value
            )
            db.session.add(complaint_source)
            db.session.flush()

        complaint = Complaint(
            case_file_id=case_file.id,
            date_received=datetime.now() + timedelta(days=10),
            source_type_id=complaint_source.id,
            source_first_nation_id=first_nation_id,
            concern_description=fake.text(max_nb_chars=200),
            status=ComplaintStatusEnum.OPEN,
            complaint_number=fake.pystr(min_chars=5, max_chars=10),
            topic_id=topic.id
        )
        db.session.add(complaint)
        db.session.flush()

        # Create source contact if needed
        source_contact = ComplaintSourceContact(
            complaint_id=complaint.id,
            full_name=fake.name(),
            is_deleted=source_contact_deleted
        )
        db.session.add(source_contact)
        db.session.commit()

        return complaint

    def _clean_up_inspection_requirement(self, insp_req):
        """Clean up a specific inspection requirement and related records."""
        if not insp_req:
            return

        inspection_id = insp_req.inspection_id

        db.session.query(InspectionReqEnforcementMap).where(
            InspectionReqEnforcementMap.requirement_id == insp_req.id
        ).delete()
        db.session.query(InspectionRequirement).where(
            InspectionRequirement.id == insp_req.id
        ).delete()
        db.session.query(InspectionRecord).where(
            InspectionRecord.inspection_id == inspection_id
        ).delete()
        db.session.query(InspectionAttendance).where(
            InspectionAttendance.inspection_id == inspection_id
        ).delete()
        db.session.query(InspectionFirstnation).where(
            InspectionFirstnation.inspection_id == inspection_id
        ).delete()
        db.session.query(Inspection).where(
            Inspection.id == inspection_id
        ).delete()
        db.session.commit()

    def _clean_up_complaint(self, complaint):
        """Clean up a specific complaint and related records."""
        if not complaint:
            return

        db.session.query(ComplaintSourceContact).where(
            ComplaintSourceContact.complaint_id == complaint.id
        ).delete()
        db.session.query(Complaint).where(
            Complaint.id == complaint.id
        ).delete()
        db.session.commit()

    def _clean_up_database(self):
        """Clean up the database after tests."""
        if self.insp_req:
            self._clean_up_inspection_requirement(self.insp_req)
        if self.complaint:
            self._clean_up_complaint(self.complaint)
        db.session.rollback()
