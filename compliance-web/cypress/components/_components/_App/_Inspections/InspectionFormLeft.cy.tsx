/// <reference types="cypress" />
import { mount } from "cypress/react";
import InspectionFormLeft from "@/components/App/Inspections/InspectionFormLeft"; // Adjust the path accordingly
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FormProvider, useForm } from "react-hook-form";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs"; // Use your chosen date adapter

// Mock data for the form inputs
const mockProjectStatusList = [
  { id: "1", name: "Project Status Alpha" },
  { id: "2", name: "Project Status Beta" },
];

const mockInitiations = [
  { id: "1", name: "Initiation Alpha" },
  { id: "2", name: "Initiation Beta" },
];

const mockStaffUsers = [
  { id: 1, name: "John Doe", is_active: true },
  { id: 2, name: "Jane Smith", is_active: true },
];

const mockIRTypes = [
  { id: "1", name: "IR Type Alpha" },
  { id: "2", name: "IR Type Beta" },
];

describe("InspectionFormLeft Component", () => {
  const setup = () => {
    const queryClient = new QueryClient();

    // Create a wrapper component to provide react-hook-form and LocalizationProvider context
    const Wrapper = ({ children }: { children: React.ReactNode }) => {
      const methods = useForm({
        defaultValues: {
          project: null,
          locationDescription: "",
          utm: "",
          primaryOfficer: null,
          officers: [],
          irTypes: [],
          dateRange: [null, null],
          initiation: null,
        },
      });

      return (
        <QueryClientProvider client={queryClient}>
          <FormProvider {...methods}>
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              {children}
            </LocalizationProvider>
          </FormProvider>
        </QueryClientProvider>
      );
    };

    mount(
      <Wrapper>
        <InspectionFormLeft
          initiationList={mockInitiations}
          staffUsersList={mockStaffUsers}
          irTypeList={mockIRTypes}
          projectStatusList={mockProjectStatusList}
        />
      </Wrapper>
    );
  };

  beforeEach(() => {
    setup();
  });

  it("renders the form with all fields", () => {
    // Check that all the labels exist
    cy.contains("Location Description").should("exist");
    cy.contains("UTM").should("exist");
    cy.contains("Primary").should("exist");
    cy.contains("Type").should("exist");
    cy.contains("Start Date").should("exist");
    cy.contains("End Date").should("exist");
    cy.contains("Initiation").should("exist");
  });

  it("allows entering a location description", () => {
    cy.get('textarea[name="locationDescription"]').type("Inspection at Site A");
    cy.get('textarea[name="locationDescription"]').should(
      "have.value",
      "Inspection at Site A"
    );
  });

  it("allows entering UTM coordinates", () => {
    cy.get('input[name="utm"]').type("9U 454135 6399452");
    cy.get('input[name="utm"]').should("have.value", "9U 454135 6399452");
  });

  it("allows selecting primary officer", () => {
    cy.get('input[name="primaryOfficer"]').click();
    cy.get("li").contains("John Doe").click();
    cy.get('input[name="primaryOfficer"]').should("have.value", "John Doe");
  });

  it("allows selecting multiple IR types", () => {
    cy.get('input[name="irTypes"]').click();
    cy.get("li").contains("IR Type Alpha").click();
    cy.get("li").contains("IR Type Beta").click();

    // Verify that both selected IR types appear as tags
    cy.get('.MuiAutocomplete-root[name="irTypes"]').within(() => {
      cy.get(".MuiAutocomplete-tag").should("have.length", 2);
      cy.get(".MuiAutocomplete-tag")
        .eq(0)
        .should("contain.text", "IR Type Alpha");
      cy.get(".MuiAutocomplete-tag")
        .eq(1)
        .should("contain.text", "IR Type Beta");
    });
  });

  it("allows selecting a date range", () => {

    cy.get('.cy-start-date').should("exist");
    cy.get('.cy-end-date').should("exist");

    // Open start date picker and wait for calendar to be visible
    cy.get('.cy-start-date button[aria-label="Choose date"]').click();
    cy.get(".MuiDateCalendar-root").should("be.visible");
    
    // Use regex to match exactly "10" (avoids matching "2026" in header)
    cy.get(".MuiPickersDay-root").contains(/^10$/).click();
    
    // Wait for calendar to close before proceeding
    cy.get(".MuiDateCalendar-root").should("not.exist");
    cy.get('.cy-start-date input').should("contain.value", "10");

    // Open end date picker and wait for calendar to be visible
    cy.get('.cy-end-date button[aria-label="Choose date"]').click();
    cy.get(".MuiDateCalendar-root").should("be.visible");
    
    // Use regex to match exactly "20"
    cy.get(".MuiPickersDay-root").contains(/^20$/).click();
    
    // Wait for calendar to close and verify value
    cy.get(".MuiDateCalendar-root").should("not.exist");
    cy.get('.cy-end-date input').should("contain.value", "20");
  });

  it("allows selecting initiation", () => {
    cy.get('input[name="initiation"]').click();
    cy.get("li").contains("Initiation Beta").click();
    cy.get('input[name="initiation"]').should("have.value", "Initiation Beta");
  });

  it("allows selecting Project Status", () => {
    cy.get('input[name="projectStatus"]').click();
    cy.get("li").contains("Project Status Beta").click();
    cy.get('input[name="projectStatus"]').should(
      "have.value",
      "Project Status Beta"
    );
  });
});
