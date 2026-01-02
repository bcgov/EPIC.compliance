/// <reference types="cypress" />
import { useModal } from "@/store/modalStore";
import { Box } from "@mui/material";
import { mount } from "cypress/react";
import { act } from "react";

const TestComponent = () => {
  const { isOpen, modalContent, setOpen, setClose } = useModal();

  return (
    <div>
      <div data-cy="modal-status">{isOpen ? "Open" : "Closed"}</div>
      <div data-cy="modal-content">{modalContent}</div>
      <button
        data-cy="open-modal"
        onClick={() =>
          setOpen({
            content: <Box data-cy="test-modal-content">Test Modal Content</Box>,
          })
        }
      >
        Open Modal
      </button>
      <button data-cy="close-modal" onClick={setClose}>
        Close Modal
      </button>
    </div>
  );
};

describe("useModal Store", () => {
  beforeEach(() => {
    mount(<TestComponent />);
  });

  it("should initialize with modal closed and no content", () => {
    cy.get('[data-cy="modal-status"]').should("contain", "Closed");
    cy.get('[data-cy="modal-content"]').should("be.empty");
  });

  it("should open the modal and display content when setOpen is called", () => {
    cy.get('[data-cy="open-modal"]').click();

    cy.get('[data-cy="modal-status"]').should("contain", "Open");
    cy.get('[data-cy="test-modal-content"]').should(
      "contain",
      "Test Modal Content"
    );
  });

  it("should close the modal and clear content when setClose is called", () => {
    cy.get('[data-cy="open-modal"]').click();
    cy.get('[data-cy="close-modal"]').click();

    cy.get('[data-cy="modal-status"]').should("contain", "Closed");
    cy.get('[data-cy="modal-content"]').should("be.empty");
  });

  it("should not open the modal if no content is provided", () => {
    act(() => {
      useModal.getState().setOpen({ content: null });
    });

    cy.get('[data-cy="modal-status"]').should("contain", "Closed");
    cy.get('[data-cy="modal-content"]').should("be.empty");
  });
});
