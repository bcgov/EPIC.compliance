/// <reference types="cypress" />
import { mount } from "cypress/react";
import RequirementSourceForm from "@/components/App/Complaints/RequirementSourceForm";
import { FormProvider, useForm } from "react-hook-form";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { RequirementSource } from "@/models/RequirementSource";
import { RequirementSourceEnum, OrderStatusEnum } from "@/utils/constants";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import DrawerProvider from "@/components/Shared/Drawer/DrawerProvider";
import { Complaint } from "@/models/Complaint";

// Mock data
const mockRequirementSources: RequirementSource[] = [
  { id: RequirementSourceEnum.ORDER, name: "Order", source_title: "Order" },
  {
    id: RequirementSourceEnum.SCHEDULE_B,
    name: "Schedule B",
    source_title: "Schedule B",
  },
  { id: RequirementSourceEnum.EAC, name: "EAC", source_title: "EAC" },
  {
    id: RequirementSourceEnum.ACT2018,
    name: "Act 2018",
    source_title: "Act 2018",
  },
  { id: RequirementSourceEnum.OTHER, name: "Other", source_title: "Other" },
];

const mockOrders = [
  { id: 1, order_number: "ORD-001", order_status: { id: OrderStatusEnum.OPEN, name: "Open" } },
  { id: 2, order_number: "ORD-002", order_status: { id: OrderStatusEnum.OPEN, name: "Open" } },
  { id: 3, order_number: "ORD-003", order_status: { id: OrderStatusEnum.OPEN, name: "Open" } },
];

const mockComplaint: Partial<Complaint> = {
  id: 1,
  complaint_number: "COMP-001",
  requirement_source_id: RequirementSourceEnum.ORDER as unknown as number,
  requirement_source: {
    id: RequirementSourceEnum.ORDER,
    name: "Order",
    source_title: "Order",
  },
  requirement_detail: {
    id: 1,
    complaint_id: 1,
    order_number: "ORD-001",
  },
};

describe("RequirementSourceForm Component", () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  beforeEach(() => {
    // Reset the query client before each test
    queryClient.clear();

    // Mock the API endpoint
    cy.intercept('GET', '**/api/orders/projectwise*', {
      statusCode: 200,
      body: mockOrders
    }).as('getOrdersProjectwise');

    // Also pre-populate the query cache
    queryClient.setQueryData(["inspection-orders-projectwise", 1], mockOrders);
  });

  const setup = (
    initialValues = {},
    complaint?: Partial<Complaint>,
    caseFileId = 1
  ) => {
    // Create a wrapper component to provide react-hook-form context
    const Wrapper = ({ children }: { children: React.ReactNode }) => {
      const methods = useForm({
        defaultValues: {
          requirementSource: null,
          order: null,
          requirementSourceDescription: "",
          ...initialValues,
        },
      });

      return (
        <QueryClientProvider client={queryClient}>
          <DrawerProvider />
          <ModalProvider />
          <FormProvider {...methods}>{children}</FormProvider>
        </QueryClientProvider>
      );
    };

    mount(
      <Wrapper>
        <RequirementSourceForm
          requirementSourceList={mockRequirementSources}
          complaint={complaint as Complaint}
          caseFileId={caseFileId}
        />
      </Wrapper>
    );
  };

  it("renders the requirement source dropdown", () => {
    setup();
    cy.contains("Requirement Source").should("exist");
  });

  it("shows order field when Order source is selected", () => {
    setup();

    // Select Order as requirement source
    cy.get('input[name="requirementSource"]').click();
    cy.get("li").contains("Order").click();

    // Check if Order field appears
    cy.contains("Order").should("exist");
    cy.get('input[name="order"]').should("exist");
  });

  it("shows requirement details field when non-Order source is selected", () => {
    setup();

    // Select Schedule B as requirement source
    cy.get('input[name="requirementSource"]').click();
    cy.get("li").contains("Schedule B").click();

    // Check if Requirement Details field appears
    cy.contains("Requirement Details").should("exist");
    cy.get('textarea[name="requirementSourceDescription"]').should("exist");
  });

  it("shows order autocomplete field when Order source is selected", () => {
    setup();

    // Select Order as requirement source
    cy.get('input[name="requirementSource"]').click();
    cy.get("li").contains("Order").click();

    // Wait for the order field to appear and verify it's an autocomplete
    cy.get('input[name="order"]').should("be.visible");
    cy.get('input[name="order"]').should("have.attr", "autocomplete", "off");

    // Verify the field is enabled and can receive input
    cy.get('input[name="order"]').should("not.be.disabled");
    cy.get('input[name="order"]').type("test");
    cy.get('input[name="order"]').should("have.value", "test");
  });

  it("allows entering requirement details for non-Order sources", () => {
    setup();

    // Select EAC as requirement source
    cy.get('input[name="requirementSource"]').click();
    cy.get("li").contains("EAC").click();

    // Enter requirement details
    cy.get('textarea[name="requirementSourceDescription"]').type(
      "Test requirement details"
    );

    // Verify entered value
    cy.get('textarea[name="requirementSourceDescription"]').should(
      "have.value",
      "Test requirement details"
    );
  });

  it("initializes order field when complaint has order_number", () => {
    // Pre-set the requirement source to ORDER so the initialization effect can run
    const initialValues = {
      requirementSource: mockRequirementSources.find(rs => rs.id === RequirementSourceEnum.ORDER)
    };
    setup(initialValues, mockComplaint as Complaint);

    // Wait for the order field to appear
    cy.get('input[name="order"]').should("be.visible");

    // Wait for data to load and initialization to complete
    cy.wait(500);

    // The order field should be pre-populated with the matching order
    cy.get('input[name="order"]').should("have.value", "ORD-001");
  });

  it("shows confirmation modal when changing requirement source with existing data", () => {
    setup();

    // Select EAC and enter some data
    cy.get('input[name="requirementSource"]').click();
    cy.get("li").contains("EAC").click();
    cy.get('textarea[name="requirementSourceDescription"]').type(
      "Some details"
    );

    // Try to change to Order
    cy.get('input[name="requirementSource"]').click();
    cy.get("li").contains("Order").click();

    // Should show confirmation modal
    cy.contains("Change Requirement Source?").should("exist");
    cy.contains(
      "You have entered information for the current requirement source"
    ).should("exist");
  });
});
