/// <reference types="cypress" />
import { mount } from "cypress/react18";
import ComplaintSourceForm from "@/components/App/Complaints/ComplaintSourceForm";
import { FormProvider, useForm } from "react-hook-form";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ComplaintSource } from "@/models/ComplaintSource";
import { Agency } from "@/models/Agency";
import { FirstNation } from "@/models/FirstNation";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import DrawerProvider from "@/components/Shared/Drawer/DrawerProvider";

// Mock data
const mockComplaintSources: ComplaintSource[] = [
  { id: "1", name: "Public" },
  { id: "2", name: "First Nation" },
  { id: "3", name: "Agency" },
  { id: "4", name: "Other" },
];

const mockAgencies: Agency[] = [
  { id: 1, name: "Agency 1" },
  { id: 2, name: "Agency 2" },
];

const mockFirstNations: FirstNation[] = [
  { id: 1, name: "First Nation 1" },
  { id: 2, name: "First Nation 2" },
];

describe("ComplaintSourceForm Component", () => {
  const setup = (initialValues = {}) => {
    const queryClient = new QueryClient();

    // Create a wrapper component to provide react-hook-form context
    const Wrapper = ({ children }: { children: React.ReactNode }) => {
      const methods = useForm({
        defaultValues: {
          complaintSource: null,
          agency: null,
          firstNation: null,
          otherDescription: "",
          contactFullName: "",
          contactTitle: "",
          contactEmail: "",
          contactPhoneNumber: "",
          contactComments: "",
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
        <ComplaintSourceForm
          complaintSourceList={mockComplaintSources}
          agenciesList={mockAgencies}
          firstNationsList={mockFirstNations}
        />
      </Wrapper>
    );
  };

  it("renders the complaint source dropdown", () => {
    setup();
    cy.contains("Complaint Source").should("exist");
  });

  it("shows agency field when Agency source is selected", () => {
    setup();

    // Select Agency as complaint source
    cy.get('input[name="complaintSource"]').click();
    cy.get("li").contains("Agency").click();

    // Check if Agency field appears
    cy.contains("Agency").should("exist");
    cy.get('input[name="agency"]').should("exist");
  });

  it("shows First Nation field when First Nation source is selected", () => {
    setup();

    // Select First Nation as complaint source
    cy.get('input[name="complaintSource"]').click();
    cy.get("li").contains("First Nation").click();

    // Check if First Nation field appears
    cy.contains("First Nation").should("exist");
    cy.get('input[name="firstNation"]').should("exist");
  });

  it("shows Description field when Other source is selected", () => {
    setup();

    // Select Other as complaint source
    cy.get('input[name="complaintSource"]').click();
    cy.get("li").contains("Other").click();

    // Check if Description field appears
    cy.contains("Description").should("exist");
    cy.get('textarea[name="otherDescription"]').should("exist");
  });

  it("shows contact form fields for any selected source", () => {
    setup();

    // Select any complaint source
    cy.get('input[name="complaintSource"]').click();
    cy.get("li").contains("Public").click();

    // Check if contact form fields appear
    cy.get('input[name="contactFullName"]').should("exist");
    cy.get('input[name="contactTitle"]').should("exist");
    cy.get('input[name="contactEmail"]').should("exist");
    cy.get('input[name="contactPhoneNumber"]').should("exist");
    cy.get('textarea[name="contactComments"]').should("exist");
  });

  it("allows selecting an agency from the dropdown", () => {
    setup();

    // Select Agency as complaint source
    cy.get('input[name="complaintSource"]').click();
    cy.get("li").contains("Agency").click();

    // Select an agency
    cy.get('input[name="agency"]').click();
    cy.get("li").contains("Agency 1").click();

    // Verify selection
    cy.get('input[name="agency"]').should("have.value", "Agency 1");
  });

  it("allows selecting a first nation from the dropdown", () => {
    setup();

    // Select First Nation as complaint source
    cy.get('input[name="complaintSource"]').click();
    cy.get("li").contains("First Nation").click();

    // Select a first nation
    cy.get('input[name="firstNation"]').click();
    cy.get("li").contains("First Nation 1").click();

    // Verify selection
    cy.get('input[name="firstNation"]').should("have.value", "First Nation 1");
  });

  it("allows entering contact information", () => {
    setup();

    // Select any complaint source
    cy.get('input[name="complaintSource"]').click();
    cy.get("li").contains("Public").click();

    // Enter contact information
    cy.get('input[name="contactFullName"]').type("John Doe");
    cy.get('input[name="contactTitle"]').type("Mr.");
    cy.get('input[name="contactEmail"]').type("john@example.com");
    cy.get('input[name="contactPhoneNumber"]').type("123-456-7890");
    cy.get('textarea[name="contactComments"]').type("Test comment");

    // Verify entered values
    cy.get('input[name="contactFullName"]').should("have.value", "John Doe");
    cy.get('input[name="contactTitle"]').should("have.value", "Mr.");
    cy.get('input[name="contactEmail"]').should(
      "have.value",
      "john@example.com"
    );
    cy.get('input[name="contactPhoneNumber"]').should(
      "have.value",
      "(123) 456-7890"
    );
    cy.get('textarea[name="contactComments"]').should(
      "have.value",
      "Test comment"
    );
  });
});
