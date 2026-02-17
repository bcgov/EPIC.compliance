"""Test project_compliance report service."""
from datetime import datetime, timedelta
from faker import Faker
import pytest
from sqlalchemy import text

from compliance_api.models import db
from compliance_api.models.case_file import CaseFile
from compliance_api.models.compliance_finding import ComplianceFindingOption
from compliance_api.models.inspection.inspection import Inspection
from compliance_api.models.inspection.inspection_req_enforcement_map import InspectionReqEnforcementMap
from compliance_api.models.inspection.inspection_requirement import InspectionRequirement
from compliance_api.models.inspection_record import InspectionRecord
from compliance_api.models.project import Project
from compliance_api.models.staff_user import StaffUser
from compliance_api.models.topic import Topic
from compliance_api.services.report import project_compliance

fake = Faker()


class TestProjectComplianceReportGenerator:
    """Test Project Compliance Report Generator."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Fixture to execute before and after each test."""
        # Clean tables before test
        db.session.execute(text('TRUNCATE projects RESTART IDENTITY CASCADE'))
        db.session.commit()

        self.project = self._create_test_project()
        self.insp_req = self._create_test_inspection_requirement(self.project.id)

        yield

        # Clean tables after test
        db.session.execute(text('TRUNCATE projects RESTART IDENTITY CASCADE'))
        db.session.commit()

    def test_initialization_with_project_id(self):
        """Test that the generator initializes correctly with a project ID."""
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id
        })
        assert generator.project_id == self.project.id
        assert generator.start_date is None
        assert generator.end_date is None

    def test_initialization_without_project_id_raises_error(self):
        """Test that initialization without project ID raises ValueError."""
        with pytest.raises(ValueError, match="Project ID must be provided"):
            project_compliance.ProjectComplianceReportGenerator({})

    def test_initialization_with_date_range(self):
        """Test that the generator initializes correctly with date range."""
        start_date = datetime.now().date()
        end_date = (datetime.now() + timedelta(days=30)).date()

        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id,
            "start_date": start_date,
            "end_date": end_date
        })

        assert generator.start_date is not None
        assert generator.end_date is not None

    def test_build_inspection_requirements_query_no_date_range(self):
        """Test building inspection requirements query with no date range."""
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id
        })
        results = generator._build_inspection_requirements_query(self.project.id).all()
        assert len(results) == 1
        assert results[0].InspectionRequirement.id == self.insp_req.id

    def test_build_inspection_requirements_query_results_expected_within_date_range(self):
        """Test building inspection requirements query with date range that includes data."""
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id,
            "start_date": (datetime.now() + timedelta(days=150)).date(),
            "end_date": (datetime.now() + timedelta(days=153)).date()
        })
        results = generator._build_inspection_requirements_query(self.project.id).all()
        assert len(results) == 1
        assert results[0].InspectionRequirement.id == self.insp_req.id

    def test_build_inspection_requirements_query_no_results_expected_with_start_date(self):
        """Test building inspection requirements query with start date that excludes data."""
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id,
            "start_date": (datetime.now() + timedelta(days=200)).date()
        })
        results = generator._build_inspection_requirements_query(self.project.id).all()
        assert len(results) == 0

    def test_build_inspection_requirements_query_no_results_expected_with_end_date(self):
        """Test building inspection requirements query with end date that excludes data."""
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id,
            "end_date": (datetime.now() - timedelta(days=10)).date()
        })
        results = generator._build_inspection_requirements_query(self.project.id).all()
        assert len(results) == 0

    def test_build_inspection_requirements_query_filters_by_project(self):
        """Test that query only returns requirements for the specified project."""
        # Create another project with inspection requirement
        other_project = self._create_test_project()
        other_insp_req = self._create_test_inspection_requirement(other_project.id)

        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id
        })
        results = generator._build_inspection_requirements_query(self.project.id).all()

        # Should only return requirements for the specified project
        assert len(results) == 1
        assert results[0].InspectionRequirement.id == self.insp_req.id
        assert results[0].InspectionRequirement.id != other_insp_req.id

        # Clean up
        self._clean_up_inspection_requirement(other_insp_req)
        db.session.query(Project).where(Project.id == other_project.id).delete()
        db.session.flush()

    def test_format_inspection_requirements_data(self):
        """Test formatting of inspection requirements data."""
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id
        })
        results = generator._build_inspection_requirements_query(self.project.id).all()
        formatted_data = generator._format_inspection_requirements_data(results)

        assert len(formatted_data) == 1
        item = formatted_data[0]

        # Check that all expected fields are present
        assert "ir_number" in item
        assert "topic_name" in item
        assert "summary" in item
        assert "start_date" in item
        assert "end_date" in item
        assert "initiation" in item
        assert "ir_progress" in item
        assert "inspection_type" in item
        assert "compliance_finding" in item
        assert "enforcement_action" in item
        assert "enforcement_status" in item
        assert "primary_officer" in item
        assert "inspection_status" in item

    def test_generate_returns_excel_file(self):
        """Test that generate method returns Excel file bytes."""
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id
        })
        result = generator.generate()

        # Check that result is bytes (Excel file)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def _create_test_project(self):
        """Create a project for testing."""
        project = Project(
            name=fake.company(),
        )
        db.session.add(project)
        db.session.flush()
        return project

    def _create_test_inspection_requirement(self, project_id):
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
            case_file_id=case_file.id,
            project_id=project_id  # Link to project
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
        db.session.flush()

        return insp_req

    def _clean_up_inspection_requirement(self, insp_req):
        """Help clean up a specific inspection requirement."""
        db.session.query(InspectionReqEnforcementMap).where(
            InspectionReqEnforcementMap.requirement_id == insp_req.id
        ).delete()
        db.session.query(InspectionRequirement).where(
            InspectionRequirement.id == insp_req.id
        ).delete()
        db.session.query(InspectionRecord).where(
            InspectionRecord.inspection_id == insp_req.inspection_id
        ).delete()
        db.session.query(Inspection).where(
            Inspection.id == insp_req.inspection_id
        ).delete()
        db.session.flush()

    def _clean_up_database(self):
        """Clean up the database after tests."""
        db.session.rollback()
