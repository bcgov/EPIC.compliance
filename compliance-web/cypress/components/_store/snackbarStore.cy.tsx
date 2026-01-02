/// <reference types="cypress" />
import { mount } from "cypress/react";
import { useSnackbar, notify } from "@/store/snackbarStore";

describe("Snackbar Zustand Store", () => {
  // A simple React component to access and display the state
  const TestComponent: React.FC = () => {
    const { isOpen, severity, message, setClose } = useSnackbar();

    return (
      <div>
        {isOpen && (
          <div className={`snackbar snackbar-${severity}`}>
            <span>{message}</span>
            <button onClick={setClose}>Close</button>
          </div>
        )}
      </div>
    );
  };

  beforeEach(() => {
    mount(<TestComponent />);
  });

  it("should open the snackbar with success severity", () => {
    notify.success("Success message");
    cy.get(".snackbar-success").should("exist").and("contain", "Success message");
  });

  it("should open the snackbar with error severity", () => {
    notify.error("Error message");
    cy.get(".snackbar-error").should("exist").and("contain", "Error message");
  });

  it("should open the snackbar with warning severity", () => {
    notify.warning("Warning message");
    cy.get(".snackbar-warning").should("exist").and("contain", "Warning message");
  });

  it("should open the snackbar with info severity", () => {
    notify.info("Info message");
    cy.get(".snackbar-info").should("exist").and("contain", "Info message");
  });

  it("should close the snackbar", () => {
    notify.success("Close test");
    cy.get(".snackbar-success").should("exist").and("contain", "Close test");
    cy.get("button").click();
    cy.get(".snackbar").should("not.exist");
  });
});
