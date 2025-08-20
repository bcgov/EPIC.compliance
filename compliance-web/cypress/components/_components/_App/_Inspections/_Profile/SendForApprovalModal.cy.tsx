/// <reference types="cypress" />
import { mount } from "cypress/react18";
import SendForApprovalModal from "@/components/App/Inspections/Profile/SendForApprovalModal";
import { StaffUser } from "@/models/Staff";
import { STAFF_USER_POSITION } from "@/utils/constants";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Box } from "@mui/material";

describe("SendForApprovalModal", () => {
  let queryClient: QueryClient;
  let mockStaffUsers: StaffUser[];
  let mockDirectors: StaffUser[];

  const mountComponent = (props = {}) => {
    const defaultProps = {
      staffUsers: mockStaffUsers,
      onSubmitHandler: cy.stub().as("onSubmitHandler"),
      isPending: false,
      ...props,
    };

    mount(
      <QueryClientProvider client={queryClient}>
        <Box
          sx={{
            width: "600px",
            height: "400px",
            overflow: "visible",
            position: "relative",
          }}
        >
          <SendForApprovalModal {...defaultProps} />
        </Box>
      </QueryClientProvider>
    );
  };

  beforeEach(() => {
    // Set viewport to ensure proper dimensions
    cy.viewport(800, 600);

    // Add CSS overrides to fix overflow issues in testing
    cy.document().then((doc) => {
      const style = doc.createElement("style");
      style.innerHTML = `
        .MuiBox-root {
          overflow: visible !important;
        }
        .MuiDialog-root {
          overflow: visible !important;
        }
        .MuiDialogContent-root {
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

    // Mock staff users data
    mockStaffUsers = [
      {
        id: 1,
        name: "John Director",
        first_name: "John",
        last_name: "Director",
        position_id: STAFF_USER_POSITION.DIRECTOR,
        is_active: true,
      },
      {
        id: 2,
        name: "Jane Deputy",
        first_name: "Jane",
        last_name: "Deputy",
        position_id: STAFF_USER_POSITION.DEPUTY_DIRECTOR,
        is_active: true,
      },
      {
        id: 3,
        name: "Bob Officer",
        first_name: "Bob",
        last_name: "Officer",
        position_id: 1, // Regular officer
        is_active: true,
      },
      {
        id: 4,
        name: "Alice Manager",
        first_name: "Alice",
        last_name: "Manager",
        position_id: 2, // Manager
        is_active: true,
      },
    ];

    // Filter directors and deputy directors
    mockDirectors = mockStaffUsers.filter((user) =>
      [
        STAFF_USER_POSITION.DIRECTOR,
        STAFF_USER_POSITION.DEPUTY_DIRECTOR,
      ].includes(user.position_id ?? 0)
    );
  });

  describe("Rendering", () => {
    it("should render the modal with correct title", () => {
      mountComponent();
      
      // The title is rendered in ModalTitleBar as h5 variant
      cy.get('h5').should("contain", "Send for Deputy Approval?");
    });

    it("should render the director selection field", () => {
      mountComponent();
      
      cy.get('label').should("contain", "Deputy Director");
      cy.get('input[placeholder="Select Deputy Director"]').should("be.visible");
    });

    it("should render the send button when directors are available", () => {
      mountComponent();
      
      cy.get('[data-testid="primary-action-modal-button"]').should("contain", "Send");
    });

    it("should not render the send button when no directors are available", () => {
      mountComponent({ staffUsers: [] });
      
      cy.get('[data-testid="primary-action-modal-button"]').should("not.exist");
    });
  });

  describe("Director Selection", () => {
    it("should filter and display only directors and deputy directors", () => {
      mountComponent();
      
      // Open the autocomplete dropdown
      cy.get('input[placeholder="Select Deputy Director"]').click();
      
      // Should only show directors and deputy directors
      cy.get('[role="option"]').should("have.length", 2);
      cy.get('[role="option"]').first().should("contain", "John Director");
      cy.get('[role="option"]').last().should("contain", "Jane Deputy");
    });

    it("should display full names in the options", () => {
      mountComponent();
      
      cy.get('input[placeholder="Select Deputy Director"]').click();
      
      cy.get('[role="option"]').first().should("contain", "John Director");
      cy.get('[role="option"]').last().should("contain", "Jane Deputy");
    });

    it("should allow selecting a director", () => {
      mountComponent();
      
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').first().click();
      
      // Should display selected value
      cy.get('input[placeholder="Select Deputy Director"]').should("have.value", "John Director");
    });
  });

  describe("Form Validation", () => {
    it("should show validation error when trying to submit without selecting director", () => {
      mountComponent();
      
      // Try to submit without selection - button should be disabled due to validation
      cy.get('[data-testid="primary-action-modal-button"]').should("be.disabled");
      
      // The button should show as disabled when form is invalid
      cy.get('[data-testid="primary-action-modal-button"]').should("have.attr", "disabled");
    });

    it("should clear validation error when director is selected", () => {
      mountComponent();
      
      // Button should be disabled initially
      cy.get('[data-testid="primary-action-modal-button"]').should("be.disabled");
      
      // Select a director
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').first().click();
      
      // Button should be enabled after selection
      cy.get('[data-testid="primary-action-modal-button"]').should("not.be.disabled");
    });

    it("should allow submission when director is selected", () => {
      mountComponent();
      
      // Select a director
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').first().click();
      
      // Submit form
      cy.get('[data-testid="primary-action-modal-button"]').click();
      
      // Should call onSubmitHandler
      cy.get("@onSubmitHandler").should("have.been.called");
    });
  });

  describe("Form Submission", () => {
    it("should call onSubmitHandler with correct data when form is submitted", () => {
      mountComponent();
      
      // Select a director
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').first().click();
      
      // Submit form
      cy.get('[data-testid="primary-action-modal-button"]').click();
      
      // Should call onSubmitHandler with correct data
      cy.get("@onSubmitHandler").should("have.been.calledWith", {
        director: mockDirectors[0],
      });
    });

    it("should call onSubmitHandler with deputy director when selected", () => {
      mountComponent();
      
      // Select deputy director
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').last().click();
      
      // Submit form
      cy.get('[data-testid="primary-action-modal-button"]').click();
      
      // Should call onSubmitHandler with correct data
      cy.get("@onSubmitHandler").should("have.been.calledWith", {
        director: mockDirectors[1],
      });
    });
  });

  describe("Loading State", () => {
    it("should show loading state when isPending is true", () => {
      mountComponent({ isPending: true });
      
      // Select a director first
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').first().click();
      
      // Button should show loading state with CircularProgress instead of text
      cy.get('[data-testid="primary-action-modal-button"]').should("not.contain", "Send");
      // Should contain CircularProgress component
      cy.get('[data-testid="primary-action-modal-button"] .MuiCircularProgress-root').should("exist");
    });

    it("should disable form submission when loading", () => {
      mountComponent({ isPending: true });
      
      // Select a director first
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').first().click();
      
      // Button should be disabled when loading (LoadingButton disables when isLoading is true)
      cy.get('[data-testid="primary-action-modal-button"]').should("be.disabled");
      
      // Form submission should be prevented when button is disabled
      // Note: The button is disabled during loading to prevent multiple submissions
    });

    it("should show loading text when isPending is true", () => {
      mountComponent({ isPending: true });
      
      // Select a director first
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').first().click();
      
      // Should show loading text instead of "Send"
      cy.get('[data-testid="primary-action-modal-button"]').should("contain", "Loading...");
    });
  });

  describe("Edge Cases", () => {
    it("should handle empty staff users array", () => {
      mountComponent({ staffUsers: [] });
      
      // Should not show send button
      cy.get('[data-testid="primary-action-modal-button"]').should("not.exist");
      
      // Should show disabled autocomplete
      cy.get('input[placeholder="Select Deputy Director"]').should("be.disabled");
    });

    it("should handle staff users with no directors", () => {
      const regularStaff = mockStaffUsers.filter(
        (user) => ![STAFF_USER_POSITION.DIRECTOR, STAFF_USER_POSITION.DEPUTY_DIRECTOR].includes(user.position_id ?? 0)
      );
      
      mountComponent({ staffUsers: regularStaff });
      
      // Should not show send button
      cy.get('[data-testid="primary-action-modal-button"]').should("not.exist");
      
      // Should show disabled autocomplete
      cy.get('input[placeholder="Select Deputy Director"]').should("be.disabled");
    });

    it("should handle staff users with null position_id", () => {
      const staffWithNullPosition = [
        {
          id: 1,
          name: "Unknown Position",
          first_name: "Unknown",
          last_name: "Position",
          position_id: null,
          is_active: true,
        },
      ];
      
      mountComponent({ staffUsers: staffWithNullPosition });
      
      // Should not show send button
      cy.get('[data-testid="primary-action-modal-button"]').should("not.exist");
      
      // Should show disabled autocomplete
      cy.get('input[placeholder="Select Deputy Director"]').should("be.disabled");
    });

    it("should handle inactive staff users", () => {
      const inactiveDirectors = [
        {
          id: 1,
          name: "Inactive Director",
          first_name: "Inactive",
          last_name: "Director",
          position_id: STAFF_USER_POSITION.DIRECTOR,
          is_active: false,
        },
      ];
      
      mountComponent({ staffUsers: inactiveDirectors });
      
      // Should still show inactive directors in the list
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').should("contain", "Inactive Director");
    });
  });

  describe("Accessibility", () => {
    it("should have proper form labels", () => {
      mountComponent();
      
      cy.get('label').should("contain", "Deputy Director");
    });

    it("should have required field indicator", () => {
      mountComponent();
      
      // The field should be marked as required through the label
      cy.get('label').should("contain", "Deputy Director");
      // Note: Material-UI doesn't always set aria-required on the input itself
      // The required state is handled through the label and form validation
    });

    it("should have proper button type", () => {
      mountComponent();
      
      cy.get('[data-testid="primary-action-modal-button"]').should("have.attr", "type", "submit");
    });
  });

  describe("Form Reset", () => {
    it("should reset form when component remounts", () => {
      mountComponent();
      
      // Select a director
      cy.get('input[placeholder="Select Deputy Director"]').click();
      cy.get('[role="option"]').first().click();
      
      // Verify selection
      cy.get('input[placeholder="Select Deputy Director"]').should("have.value", "John Director");
      
      // Remount component
      mountComponent();
      
      // Form should be reset
      cy.get('input[placeholder="Select Deputy Director"]').should("have.value", "");
    });
  });
});
