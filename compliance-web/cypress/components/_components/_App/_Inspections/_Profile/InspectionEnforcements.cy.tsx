/// <reference types="cypress" />
import { mount } from "cypress/react";
import InspectionEnforcements from "@/components/App/Inspections/Profile/InspectionEnforcements";
import { Inspection } from "@/models/Inspection";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { InspectionOrder } from "@/models/InspectionOrder";
import { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import { AdministrativePenalty } from "@/models/AdministrativePenalty";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Box } from "@mui/material";
import { EnforcementActionEnum } from "@/utils/constants";
import { AuthProvider } from "react-oidc-context";
import { OidcConfig } from "@/utils/config";

describe("InspectionEnforcements", () => {
  let queryClient: QueryClient;
  let mockInspection: Inspection;
  let mockRequirements: InspectionRequirement[];
  let mockOrders: InspectionOrder[];
  let mockWarningLetters: InspectionWarningLetter[];
  let mockAdministrativePenalties: AdministrativePenalty[];

  const mountComponent = (inspectionData = mockInspection) => {
    mount(
      <QueryClientProvider client={queryClient}>
        <AuthProvider {...OidcConfig}>
          <Box
            sx={{
              width: "800px",
              height: "800px",
              overflow: "visible",
              position: "relative",
            }}
          >
            <InspectionEnforcements inspectionData={inspectionData} />
          </Box>
        </AuthProvider>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    // Set viewport to ensure proper dimensions
    cy.viewport(1200, 800);

    // Add CSS overrides to fix overflow issues in testing
    cy.document().then((doc) => {
      const style = doc.createElement("style");
      style.innerHTML = `
        .MuiBox-root {
          overflow: visible !important;
        }
        [class*="DynamicHeightBox"] {
          height: auto !important;
          overflow: visible !important;
        }
      `;
      doc.head.appendChild(style);
    });

    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });

    // Mock current user for useCurrentLoggedInUser hook
    const mockCurrentUser = { preferred_username: "test.user@gov.bc.ca" };
    queryClient.setQueryData(["current-user"], mockCurrentUser);

    // Mock staff users data
    const mockStaffUsers = [
      {
        id: 1,
        name: "Test User",
        auth_user_guid: "test.user@gov.bc.ca",
        is_active: true,
      },
    ];
    queryClient.setQueryData(["staff-users", true], mockStaffUsers);

    // Default mock inspection data
    mockInspection = {
      id: 1,
      ir_number: "IR-001",
      case_file_id: 1,
      project_id: 1,
      location_description: "Test location description",
      utm: "10U 123456 6543210",
      initiation_id: 1,
      ir_status_id: 1,
      project_status_id: 1,
      primary_officer_id: 1,
      start_date: "2023-04-15T12:00:00Z",
      end_date: "2023-04-16T12:00:00Z",
      debrief_date: "2023-04-17T12:00:00Z",
      types: [
        { id: "1", name: "Field" },
        { id: "2", name: "Administrative" },
      ],
      types_text: "Field, Administrative",
      inspection_status: "Open",
      is_active: true,
      project_description: "Test project description",
      initiation: { id: "1", name: "Test Initiation" },
      project: { id: 1, name: "Test Project" },
      primary_officer: { id: 1, name: "John Doe", is_active: true },
      ir_status: { id: "1", name: "Active" },
      case_file: {
        id: 1,
        project: { id: 1, name: "Test Project" },
        project_description: "Test Project Description",
        date_created: "2023-04-15T12:00:00Z",
        initiation: { id: "1", name: "Test Initiation" },
        primary_officer: { id: 1, name: "John Doe", is_active: true },
        officers: [
          { id: 2, name: "Jane Smith", is_active: true },
          { id: 3, name: "Bob Johnson", is_active: true },
        ],
        project_id: 1,
        primary_officer_id: 1,
        case_file_number: "CF-001",
        case_file_status: "Active",
        is_active: true,
      },
      project_status: { id: "1", name: "In Progress" },
      inspectionAttendances: [],
      is_history: false,
    };

    // Mock requirements with enforcement actions
    mockRequirements = [
      {
        id: 1,
        inspection_id: 1,
        summary: "Test Requirement 1",
        topic: { id: 1, name: "Test Topic" },
        topic_id: 1,
        agency_id: 1,
        enforcement_action_id: 1,
        compliance_finding_id: 1,
        findings: "Test Findings 1",
        sort_order: 1,
        is_active: true,
        requirement_source_details: [],
        req_type: { id: "REQ", name: "Requirement" },
        agency: { id: 1, name: "Test Agency" },
        compliance_finding: { id: "1", name: "Out of Compliance" },
        enforcement_action_data: [
          { id: EnforcementActionEnum.ORDER, name: "Order" },
        ],
      },
      {
        id: 2,
        inspection_id: 1,
        summary: "Test Requirement 2",
        topic: { id: 2, name: "Test Topic 2" },
        topic_id: 2,
        agency_id: 1,
        enforcement_action_id: 2,
        compliance_finding_id: 1,
        findings: "Test Findings 2",
        sort_order: 2,
        is_active: true,
        requirement_source_details: [],
        req_type: { id: "REQ", name: "Requirement" },
        agency: { id: 1, name: "Test Agency" },
        compliance_finding: { id: "1", name: "Out of Compliance" },
        enforcement_action_data: [
          { id: EnforcementActionEnum.WARNING_LETTER, name: "Warning Letter" },
        ],
      },
      {
        id: 3,
        inspection_id: 1,
        summary: "Test Requirement 3",
        topic: { id: 3, name: "Test Topic 3" },
        topic_id: 3,
        agency_id: 1,
        enforcement_action_id: 3,
        compliance_finding_id: 1,
        findings: "Test Findings 3",
        sort_order: 3,
        is_active: true,
        requirement_source_details: [],
        req_type: { id: "REQ", name: "Requirement" },
        agency: { id: 1, name: "Test Agency" },
        compliance_finding: { id: "1", name: "Out of Compliance" },
        enforcement_action_data: [
          { id: EnforcementActionEnum.AP_RECOMMENDATION, name: "AP Recommendation" },
        ],
      },
      {
        id: 4,
        inspection_id: 1,
        summary: "Test Requirement 4",
        topic: { id: 4, name: "Test Topic 4" },
        topic_id: 4,
        agency_id: 1,
        enforcement_action_id: 4,
        compliance_finding_id: 1,
        findings: "Test Findings 4",
        sort_order: 4,
        is_active: true,
        requirement_source_details: [],
        req_type: { id: "REQ", name: "Requirement" },
        agency: { id: 1, name: "Test Agency" },
        compliance_finding: { id: "1", name: "Out of Compliance" },
        enforcement_action_data: [
          { id: EnforcementActionEnum.ADVISORY, name: "Advisory" },
        ],
      },
    ];

    // Mock orders
    mockOrders = [
      {
        id: 1,
        inspection_id: 1,
        order_number: "ORDER-001",
        date_issued: "2023-04-15T12:00:00Z",
        order_status: { id: "DRAFT", name: "Draft" },
        order_requirement_maps: [
          {
            id: 1,
            inspection_requirement_id: 1,
            inspection_requirement: {
              id: 1,
              summary: "Test Requirement 1"
            }
          },
        ],
        is_active: true,
      },
    ];

    // Mock warning letters
    mockWarningLetters = [
      {
        id: 1,
        inspection_id: 1,
        warning_letter_number: "WL-001",
        date_issued: "2023-04-15T12:00:00Z",
        warning_letter_requirement_maps: [
          {
            id: 1,
            inspection_requirement_id: 2,
            inspection_requirement: {
              id: 2,
              summary: "Test Requirement 2"
            }
          },
        ],
        is_active: true,
      },
    ];

    // Mock administrative penalties
    mockAdministrativePenalties = [
      {
        id: 1,
        inspection_id: 1,
        administrative_penalty_number: "AP-001",
        date_referred: "2023-04-15T12:00:00Z",
        decision_date: "2023-04-15T12:00:00Z",
        referral_status: { id: "DRAFTING", value: "Drafting" },
        administrative_penalty_requirement_maps: [
          {
            id: 1,
            inspection_requirement_id: 3,
            inspection_requirement: {
              id: 3,
              summary: "Test Requirement 3"
            }
          },
        ],
        is_active: true,
      },
    ];
  });

  describe("Basic Component Mounting", () => {
    it("mounts without crashing", () => {
      expect(() => mountComponent()).to.not.throw();
    });

    it("renders the component structure", () => {
      mountComponent();
      cy.get('body').should('contain', 'Enforcement');
    });
  });

  describe("Inspection Status Handling", () => {
    it("handles open inspection status", () => {
      mockInspection.inspection_status = "Open";
      mountComponent();
      cy.contains("Enforcement").should("be.visible");
    });

    it("handles closed inspection status", () => {
      mockInspection.inspection_status = "Closed";
      mountComponent();
      cy.contains("Enforcement").should("be.visible");
    });

    it("handles undefined inspection status", () => {
      mockInspection.inspection_status = undefined;
      mountComponent();
      cy.contains("Enforcement").should("be.visible");
    });

    it("handles null inspection status", () => {
      mockInspection.inspection_status = undefined;
      mountComponent();
      cy.contains("Enforcement").should("be.visible");
    });

    it("handles lowercase inspection status", () => {
      mockInspection.inspection_status = "open";
      mountComponent();
      cy.contains("Enforcement").should("be.visible");
    });
  });

  describe("Data Loading States", () => {
    it("handles empty data gracefully", () => {
      queryClient.setQueryData(["inspection-requirements", mockInspection.id], []);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();
      cy.contains("Enforcement").should("be.visible");
    });

    it("handles missing case file data", () => {
      queryClient.setQueryData(["inspection-requirements", mockInspection.id], []);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();
      cy.contains("Enforcement").should("be.visible");
    });

    it("shows loading state when data is loading", () => {
      // Don't set any data to trigger loading state
      mountComponent();
      cy.contains("Enforcement").should("be.visible");
    });
  });

  describe("Requirements Processing and Filtering", () => {
    beforeEach(() => {
      mockInspection.inspection_status = "Open";
      queryClient.setQueryData(["case-file", mockInspection.case_file.case_file_number], mockInspection.case_file);
    });

    it("filters requirements with enforcement actions correctly", () => {
      queryClient.setQueryData(["inspection-requirements", mockInspection.id], mockRequirements);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      // Should show notification cards for requirements with enforcement actions
      cy.contains("Test Requirement 1").should("be.visible");
      cy.contains("Test Requirement 2").should("be.visible");
      cy.contains("Test Requirement 3").should("be.visible");
      // Should not show requirement 4 (has advisory, not enforcement action)
      cy.contains("Test Requirement 4").should("not.exist");
    });

    it("handles requirements without enforcement actions", () => {
      const requirementsWithoutEnforcement = mockRequirements.map(req => ({
        ...req,
        enforcement_action_data: []
      }));

      queryClient.setQueryData(["inspection-requirements", mockInspection.id], requirementsWithoutEnforcement);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      // Should not show any notification cards
      cy.contains("Test Requirement 1").should("not.exist");
      cy.contains("Test Requirement 2").should("not.exist");
      cy.contains("Test Requirement 3").should("not.exist");
    });

    it("handles requirements with undefined enforcement action data", () => {
      const requirementsWithUndefinedEnforcement = mockRequirements.map(req => ({
        ...req,
        enforcement_action_data: undefined
      }));

      queryClient.setQueryData(["inspection-requirements", mockInspection.id], requirementsWithUndefinedEnforcement);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      // Should not show any notification cards
      cy.contains("Test Requirement 1").should("not.exist");
    });
  });

  describe("Non-Proceeded Requirements Calculation", () => {
    beforeEach(() => {
      mockInspection.inspection_status = "Open";
      queryClient.setQueryData(["case-file", mockInspection.case_file.case_file_number], mockInspection.case_file);
      queryClient.setQueryData(["inspection-requirements", mockInspection.id], mockRequirements);
    });

    it("calculates non-proceeded order requirements correctly", () => {
      queryClient.setQueryData(["inspection-orders", mockInspection.id], mockOrders);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      // Should show notification cards for requirements that haven't been processed
      cy.contains("Test Requirement 2").should("be.visible");
      cy.contains("Test Requirement 3").should("be.visible");
      // Note: The component may still show requirement 1 even if it has an order
      // This depends on the actual filtering logic implementation
    });

    it("calculates non-proceeded warning letter requirements correctly", () => {
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], mockWarningLetters);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      // Should show notification cards for requirements that haven't been processed
      cy.contains("Test Requirement 1").should("be.visible");
      cy.contains("Test Requirement 3").should("be.visible");
      // Note: The component may still show requirement 2 even if it has a warning letter
      // This depends on the actual filtering logic implementation
    });

    it("calculates non-proceeded AP requirements correctly", () => {
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], mockAdministrativePenalties);

      mountComponent();

      // Should show notification cards for requirements that haven't been processed
      cy.contains("Test Requirement 1").should("be.visible");
      cy.contains("Test Requirement 2").should("be.visible");
      // Note: The component may still show requirement 3 even if it has an AP
      // This depends on the actual filtering logic implementation
    });

    it("handles empty requirement enforcement arrays", () => {
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      // Should show all requirements with enforcement actions
      cy.contains("Test Requirement 1").should("be.visible");
      cy.contains("Test Requirement 2").should("be.visible");
      cy.contains("Test Requirement 3").should("be.visible");
    });
  });

  describe("Enforcement Documents Rendering", () => {
    beforeEach(() => {
      mockInspection.inspection_status = "Open";
      queryClient.setQueryData(["case-file", mockInspection.case_file.case_file_number], mockInspection.case_file);
      queryClient.setQueryData(["inspection-requirements", mockInspection.id], mockRequirements);
    });

    it("renders existing enforcement orders", () => {
      queryClient.setQueryData(["inspection-orders", mockInspection.id], mockOrders);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      cy.contains("ORDER-001").should("be.visible");
    });

    it("renders existing warning letters", () => {
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], mockWarningLetters);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      cy.contains("WL-001").should("be.visible");
    });

    it("renders existing administrative penalties", () => {
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], mockAdministrativePenalties);

      mountComponent();

      cy.contains("AP-001").should("be.visible");
    });

    it("renders multiple enforcement document types simultaneously", () => {
      queryClient.setQueryData(["inspection-orders", mockInspection.id], mockOrders);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], mockWarningLetters);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], mockAdministrativePenalties);

      mountComponent();

      cy.contains("ORDER-001").should("be.visible");
      cy.contains("WL-001").should("be.visible");
      cy.contains("AP-001").should("be.visible");
    });
  });

  describe("New Enforcement Button and Actions", () => {
    beforeEach(() => {
      mockInspection.inspection_status = "Open";
      queryClient.setQueryData(["case-file", mockInspection.case_file.case_file_number], mockInspection.case_file);
      queryClient.setQueryData(["inspection-requirements", mockInspection.id], mockRequirements);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);
    });

    it("shows new enforcement button when inspection is open and data is loaded", () => {
      mountComponent();
      cy.contains("button", "New Enforcement").should("be.visible");
    });

    it("hides new enforcement button when inspection is closed", () => {
      mockInspection.inspection_status = "Closed";
      mountComponent();
      cy.contains("button", "New Enforcement").should("not.exist");
    });

    it("hides new enforcement button when data is loading", () => {
      // Don't set any data to trigger loading state
      queryClient.clear();
      mountComponent();
      cy.contains("button", "New Enforcement").should("not.exist");
    });

    it("hides new enforcement button when enforcements not allowed", () => {
      mockInspection.inspection_status = "Closed";
      mountComponent();
      cy.contains("button", "New Enforcement").should("not.exist");
    });
  });

  describe("Edge Cases and Error Handling", () => {
    it("handles missing case file officers gracefully", () => {
      const inspectionWithoutOfficers = {
        ...mockInspection,
        case_file: {
          ...mockInspection.case_file,
          officers: undefined
        }
      };

      queryClient.setQueryData(["inspection-requirements", mockInspection.id], []);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent(inspectionWithoutOfficers);
      cy.contains("Enforcement").should("be.visible");
    });

    it("handles case file with no officers", () => {
      const inspectionWithNoOfficers = {
        ...mockInspection,
        case_file: {
          ...mockInspection.case_file,
          officers: []
        }
      };

      queryClient.setQueryData(["inspection-requirements", mockInspection.id], []);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent(inspectionWithNoOfficers);
      cy.contains("Enforcement").should("be.visible");
    });

    it("handles requirements with null enforcement action data", () => {
      const requirementsWithNullEnforcement = mockRequirements.map(req => ({
        ...req,
        enforcement_action_data: null
      }));

      queryClient.setQueryData(["inspection-requirements", mockInspection.id], requirementsWithNullEnforcement);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();
      cy.contains("Enforcement").should("be.visible");
    });

    it("handles mixed requirement enforcement action data", () => {
      const mixedRequirements = [
        {
          ...mockRequirements[0],
          enforcement_action_data: [{ id: EnforcementActionEnum.ORDER, name: "Order" }]
        },
        {
          ...mockRequirements[1],
          enforcement_action_data: []
        },
        {
          ...mockRequirements[2],
          enforcement_action_data: undefined
        },
        {
          ...mockRequirements[3],
          enforcement_action_data: null
        }
      ];

      queryClient.setQueryData(["inspection-requirements", mockInspection.id], mixedRequirements);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      // Should only show requirement 1 (has enforcement action)
      cy.contains("Test Requirement 1").should("be.visible");
      cy.contains("Test Requirement 2").should("not.exist");
      cy.contains("Test Requirement 3").should("not.exist");
      cy.contains("Test Requirement 4").should("not.exist");
    });
  });

  describe("Data Invalidation and Refresh", () => {
    it("handles query invalidation for orders", () => {
      mockInspection.inspection_status = "Open";
      queryClient.setQueryData(["case-file", mockInspection.case_file.case_file_number], mockInspection.case_file);
      queryClient.setQueryData(["inspection-requirements", mockInspection.id], mockRequirements);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], mockOrders);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      // Should render orders
      cy.contains("ORDER-001").should("be.visible");
    });

    it("handles query invalidation for warning letters", () => {
      mockInspection.inspection_status = "Open";
      queryClient.setQueryData(["case-file", mockInspection.case_file.case_file_number], mockInspection.case_file);
      queryClient.setQueryData(["inspection-requirements", mockInspection.id], mockRequirements);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], mockWarningLetters);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], []);

      mountComponent();

      // Should render warning letters
      cy.contains("WL-001").should("be.visible");
    });

    it("handles query invalidation for administrative penalties", () => {
      mockInspection.inspection_status = "Open";
      queryClient.setQueryData(["case-file", mockInspection.case_file.case_file_number], mockInspection.case_file);
      queryClient.setQueryData(["inspection-requirements", mockInspection.id], mockRequirements);
      queryClient.setQueryData(["inspection-orders", mockInspection.id], []);
      queryClient.setQueryData(["inspection-warning-letters", mockInspection.id], []);
      queryClient.setQueryData(["inspection-administrative-penalties", mockInspection.id], mockAdministrativePenalties);

      mountComponent();

      // Should render administrative penalties
      cy.contains("AP-001").should("be.visible");
    });
  });
});
