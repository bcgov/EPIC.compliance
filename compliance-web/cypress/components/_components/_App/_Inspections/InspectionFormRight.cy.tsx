/// <reference types="cypress" />
import { mount } from "cypress/react";
import InspectionFormRight from "@/components/App/Inspections/InspectionFormRight";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FormProvider, useForm } from "react-hook-form";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import { useModal } from "@/store/modalStore";

// Mock data for the test

const mockAttendanceList = [
  { id: "1", name: "Agency" },
  { id: "2", name: "First Nation" },
  { id: "7", name: "Other" },
];

const mockAgenciesList = [
  { id: 1, name: "Agency Alpha" },
  { id: 2, name: "Agency Beta" },
];

const mockStaffUsers = [
  { id: 1, name: "John Doe", is_active: true },
  { id: 2, name: "Jane Smith", is_active: true },
];

const mockFirstNationsList = [
  { id: 1, name: "First Nation Alpha" },
  { id: 2, name: "First Nation Beta" },
];

describe("InspectionFormRight Component", () => {
  const setup = () => {
    const queryClient = new QueryClient();

    // Create a wrapper component to provide react-hook-form and LocalizationProvider context
    const Wrapper = ({ children }: { children: React.ReactNode }) => {
      const methods = useForm({
        defaultValues: {
          irStatus: null,
          projectStatuses: [],
          inAttendance: [],
          agencies: [],
          firstNations: [],
          other: "",
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
        <InspectionFormRight
          attendanceList={mockAttendanceList}
          agenciesList={mockAgenciesList}
          firstNationsList={mockFirstNationsList}
          staffList={mockStaffUsers}
        />
      </Wrapper>
    );
  };

  beforeEach(() => {
    useModal.setState({
      setOpen: cy.stub().as("setOpen"),
      setClose: cy.stub().as("setClose"),
    });

    setup();
  });

  it("renders the form with all fields", () => {
    cy.contains("In Attendance").should("exist");
  });

  it("allows selecting multiple attendees in the 'In Attendance' field", () => {
    cy.get('input[name="inAttendance"]').click();
    cy.get("li").contains("Agency").click();
    cy.get("li").contains("First Nation").click();

    // Verify that both selected attendees appear
    cy.get(".MuiAutocomplete-tag").should("have.length", 2);
    cy.get(".MuiAutocomplete-tag").eq(0).should("contain.text", "Agency");
    cy.get(".MuiAutocomplete-tag").eq(1).should("contain.text", "First Nation");
  });

  it("displays dynamic fields when agency attendance option is selected", () => {
    cy.get('input[name="inAttendance"]').click();
    cy.get("li").contains("Agency").click();

    cy.get("body").click(0, 0);

    // Verify that the dynamic fields appear
    cy.get('input[name="agencies"]').should("exist");
    cy.get('input[name="firstNations"]').should("not.exist");

    // Ensure these fields can select multiple options
    cy.get('input[name="agencies"]').click();
    cy.get("li").contains(mockAgenciesList[0].name).click();
    cy.get('.MuiAutocomplete-root[name="agencies"]').within(() => {
      cy.get(".MuiAutocomplete-tag").should("have.length", 1);
      cy.get(".MuiAutocomplete-tag")
        .eq(0)
        .should("contain.text", mockAgenciesList[0].name);
    });
  });

  it("displays dynamic fields when firstNation attendance option is selected", () => {
    cy.get('input[name="inAttendance"]').click();
    cy.get("li").contains("First Nation").click();

    cy.get("body").click(0, 0);

    // Verify that the dynamic fields appear
    cy.get('input[name="agencies"]').should("not.exist");
    cy.get('input[name="firstNations"]').should("exist");

    cy.get('input[name="firstNations"]').click();
    cy.get("li").contains(mockFirstNationsList[0].name).click();
    cy.get('.MuiAutocomplete-root[name="firstNations"]').within(() => {
      cy.get(".MuiAutocomplete-tag").should("have.length", 1);
      cy.get(".MuiAutocomplete-tag")
        .eq(0)
        .should("contain.text", mockFirstNationsList[0].name);
    });
  });

  it("allows entering values in text fields for 'Other'", () => {
    // Select 'Other' attendance
    cy.get('input[name="inAttendance"]').click();
    cy.get("li").contains("Other").click();

    cy.get("body").click(0, 0);

    // Verify that text fields appear
    cy.get('textarea[name="other"]')
      .should("exist")
      .type("Test Other Attendees");
    cy.get('textarea[name="other"]').should(
      "have.value",
      "Test Other Attendees"
    );
  });

  it("displays a confirmation modal when attempting to remove an option with selected items", () => {
    // Select 'Agency'
    cy.get('input[name="inAttendance"]').click();
    cy.get("li").contains("Agency").click();

    cy.get("body").click(0, 0);

    // Select an option under 'Agencies'
    cy.get('input[name="agencies"]').click();
    cy.get("li").contains("Agency Alpha").click();

    cy.get("body").click(0, 0);

    cy.get('.MuiAutocomplete-root[name="inAttendance"]').within(() => {
      cy.get(".MuiAutocomplete-tag")
        .should("contain.text", "Agency")
        .find('svg[data-testid="CancelIcon"]')
        .click();
    });

    cy.get("@setOpen").should("have.been.calledOnce");
  });
});
