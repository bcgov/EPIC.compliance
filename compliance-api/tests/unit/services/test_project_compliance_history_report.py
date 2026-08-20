"""Test project_compliance report service."""
from datetime import datetime, timedelta
from faker import Faker
import pytest
from sqlalchemy import text

from compliance_api.models import db
from compliance_api.models.administrative_penalty import (
    AdministrativePenalty, AdministrativePenaltyInspectionRequirementMap, DecisionEnum, ReferralStatusEnum)
from compliance_api.models.case_file import CaseFile
from compliance_api.models.compliance_finding import ComplianceFindingOption
from compliance_api.models.enforcement_action import EnforcementActionOptionEnum
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

    def test_linked_ap_shows_dm_decision_and_penalty_amount(self):
        """Test that linked APs display DM Decision and AP Value correctly."""
        # 1. Create second inspection with requirement
        insp_req_b = self._create_test_inspection_requirement(self.project.id)

        # 2. Update requirement B's enforcement action to AP (ID 6)
        db.session.query(InspectionReqEnforcementMap).filter(
            InspectionReqEnforcementMap.requirement_id == insp_req_b.id
        ).update({"enforcement_action_id": EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value})
        db.session.flush()

        # 3. Create AP on original inspection
        ap = self._create_administrative_penalty(
            inspection_id=self.insp_req.inspection_id,
            decision=DecisionEnum.AP_ISSUED,
            penalty_amount=5000.00
        )

        # 4. Link AP to requirement B
        ap_req_map = AdministrativePenaltyInspectionRequirementMap(
            administrative_penalty_id=ap.id,
            inspection_requirement_id=insp_req_b.id
        )
        db.session.add(ap_req_map)
        db.session.flush()

        # 5. Generate report and check
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id
        })
        results = generator._build_inspection_requirements_query(self.project.id).all()
        formatted = generator._format_inspection_requirements_data(results)

        # Find the linked AP row
        ap_rows = [r for r in formatted if r.get("enforcement_action") == "Administrative Penalty Recommendation"]
        assert len(ap_rows) >= 1

        linked_ap_row = [r for r in ap_rows if r.get("ir_number") == insp_req_b.inspection.ir_number]
        assert len(linked_ap_row) == 1
        assert linked_ap_row[0]["ap_dm_decision"] == "AP Issued"
        assert linked_ap_row[0]["ap_penalty_amount"] == 5000.00

    def test_order_row_does_not_show_ap_fields_when_requirement_has_both(self):
        """Test that Order rows don't show AP data when requirement has both Order and AP."""
        from compliance_api.models.order import Order, OrderInspectionRequirementMap

        # 1. Create requirement with BOTH Order and AP enforcement actions
        insp_req = self._create_test_inspection_requirement(self.project.id)

        # Add AP enforcement action (already has ID 1, add ID 5 for Order and ID 6 for AP)
        db.session.query(InspectionReqEnforcementMap).filter(
            InspectionReqEnforcementMap.requirement_id == insp_req.id
        ).delete()

        # Add Order enforcement action
        order_enf_map = InspectionReqEnforcementMap(
            requirement_id=insp_req.id,
            enforcement_action_id=EnforcementActionOptionEnum.ORDER.value  # 5
        )
        # Add AP enforcement action
        ap_enf_map = InspectionReqEnforcementMap(
            requirement_id=insp_req.id,
            enforcement_action_id=EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value  # 6
        )
        db.session.add_all([order_enf_map, ap_enf_map])
        db.session.flush()

        # 2. Create and link an Order
        order = Order(
            order_number=fake.pystr(min_chars=10, max_chars=15),
            inspection_id=insp_req.inspection_id,
            issuing_officer_id=fake.random_int(min=1, max=10),
        )
        db.session.add(order)
        db.session.flush()

        order_req_map = OrderInspectionRequirementMap(
            order_id=order.id,
            inspection_requirement_id=insp_req.id
        )
        db.session.add(order_req_map)
        db.session.flush()

        # 3. Create and link an AP with decision
        ap = self._create_administrative_penalty(
            inspection_id=insp_req.inspection_id,
            decision=DecisionEnum.AP_ISSUED,
            penalty_amount=7500.00
        )
        ap_req_map = AdministrativePenaltyInspectionRequirementMap(
            administrative_penalty_id=ap.id,
            inspection_requirement_id=insp_req.id
        )
        db.session.add(ap_req_map)
        db.session.flush()

        # 4. Generate report
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id
        })
        results = generator._build_inspection_requirements_query(self.project.id).all()
        formatted = generator._format_inspection_requirements_data(results)

        # 5. Find rows for this requirement by IR number
        req_rows = [r for r in formatted if r.get("ir_number") == insp_req.inspection.ir_number]
        assert len(req_rows) == 2  # Should have 2 rows: one for Order, one for AP

        order_row = next((r for r in req_rows if r.get("enforcement_action") == "Order"), None)
        ap_row = next(
            (r for r in req_rows if r.get("enforcement_action") == "Administrative Penalty Recommendation"),
            None
        )

        assert order_row is not None, "Order row should exist"
        assert ap_row is not None, "AP row should exist"

        # Order row should NOT show AP data
        assert order_row["ap_dm_decision"] is None, "Order row should not show DM Decision"
        assert order_row["ap_penalty_amount"] is None, "Order row should not show AP Value"

        # AP row SHOULD show AP data
        assert ap_row["ap_dm_decision"] == "AP Issued", "AP row should show DM Decision"
        assert ap_row["ap_penalty_amount"] == 7500.00, "AP row should show AP Value"

    def test_multiple_aps_linked_to_same_requirement_shows_all(self):
        """Test that multiple APs linked to the same requirement each get their own row."""
        # 1. Create requirement with AP enforcement action
        insp_req = self._create_test_inspection_requirement(self.project.id)

        # Update enforcement action to AP
        db.session.query(InspectionReqEnforcementMap).filter(
            InspectionReqEnforcementMap.requirement_id == insp_req.id
        ).update({"enforcement_action_id": EnforcementActionOptionEnum.ADMINISTRATIVE_PENALTY_RECOMMENDATION.value})
        db.session.flush()

        # 2. Create TWO APs with different data
        ap1 = self._create_administrative_penalty(
            inspection_id=insp_req.inspection_id,
            decision=DecisionEnum.AP_ISSUED,
            penalty_amount=1000.00
        )
        ap1.administrative_penalty_number = "AP1-TEST-001"

        ap2 = self._create_administrative_penalty(
            inspection_id=insp_req.inspection_id,
            decision=DecisionEnum.AP_NOT_PROCEEDING,
            penalty_amount=2000.00
        )
        ap2.administrative_penalty_number = "AP2-TEST-002"
        db.session.flush()

        # 3. Link BOTH APs to the same requirement
        ap_req_map1 = AdministrativePenaltyInspectionRequirementMap(
            administrative_penalty_id=ap1.id,
            inspection_requirement_id=insp_req.id
        )
        ap_req_map2 = AdministrativePenaltyInspectionRequirementMap(
            administrative_penalty_id=ap2.id,
            inspection_requirement_id=insp_req.id
        )
        db.session.add_all([ap_req_map1, ap_req_map2])
        db.session.flush()

        # 4. Generate report
        generator = project_compliance.ProjectComplianceReportGenerator({
            "project_id": self.project.id
        })
        results = generator._build_inspection_requirements_query(self.project.id).all()
        formatted = generator._format_inspection_requirements_data(results)

        # 5. Find rows for this requirement
        req_rows = [r for r in formatted if r.get("ir_number") == insp_req.inspection.ir_number]

        # EXPECTED: 2 rows, one for each AP
        assert len(req_rows) == 2, f"Expected 2 rows for 2 linked APs, got {len(req_rows)}"

        # Verify different AP data in each row
        ap_numbers = [r.get("enforcement_document_number") for r in req_rows]
        assert len(set(ap_numbers)) == 2, f"Each row should have a different AP number, got {ap_numbers}"
        assert "AP1-TEST-001" in ap_numbers, "Should include AP1 number"
        assert "AP2-TEST-002" in ap_numbers, "Should include AP2 number"

        # Verify each AP has correct decision
        ap1_row = next((r for r in req_rows if r.get("enforcement_document_number") == "AP1-TEST-001"), None)
        ap2_row = next((r for r in req_rows if r.get("enforcement_document_number") == "AP2-TEST-002"), None)

        assert ap1_row is not None, "AP1 row should exist"
        assert ap2_row is not None, "AP2 row should exist"

        assert ap1_row["ap_dm_decision"] == "AP Issued", "AP1 should show AP Issued decision"
        assert ap1_row["ap_penalty_amount"] == 1000.00, "AP1 should show $1000 penalty"

        assert ap2_row["ap_dm_decision"] == "AP Not Proceeding", "AP2 should show AP Not Proceeding decision"
        assert ap2_row["ap_penalty_amount"] is None, "AP2 should not show penalty for Not Proceeding decision"

    # Helper method:
    def _create_administrative_penalty(self, inspection_id, decision=None, penalty_amount=None):
        """Create an administrative penalty for testing."""
        ap = AdministrativePenalty(
            administrative_penalty_number=fake.pystr(min_chars=10, max_chars=15),
            inspection_id=inspection_id,
            referral_status=ReferralStatusEnum.PREPARING_REFERRAL_FOR_AEO,
            decision=decision,
            penalty_amount=penalty_amount
        )
        db.session.add(ap)
        db.session.flush()
        return ap

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
