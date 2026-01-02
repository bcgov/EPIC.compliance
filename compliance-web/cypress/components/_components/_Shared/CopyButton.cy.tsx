// cypress/components/CopyButton.cy.tsx
import { mount } from "cypress/react";
import CopyButton from "@/components/Shared/CopyButton"; // Adjust the import path if needed

describe("<CopyButton />", () => {
  const copyText = "Sample text to copy";

  beforeEach(() => {
    // Set up the clipboard stub
    cy.window().then((win) => {
      cy.stub(win.navigator.clipboard, "writeText").as("writeTextStub");
    });
  });

  it("renders CopyButton", () => {
    mount(<CopyButton copyText={copyText} />);
    cy.get("button").should("exist");
  });

  it("displays the outlined icon by default", () => {
    mount(<CopyButton copyText={copyText} />);
    cy.get("svg[data-testid='FileCopyOutlinedIcon']").should("exist");
  });

  it("displays the filled icon on hover", () => {
    mount(<CopyButton copyText={copyText} />);
    cy.get("button").trigger("mouseover");
    cy.get("svg[data-testid='FileCopyIcon']").should("exist");
    cy.get("button").trigger("mouseout");
    cy.get("svg[data-testid='FileCopyOutlinedIcon']").should("exist");
  });

  it("copies text to the clipboard on click", () => {
    mount(<CopyButton copyText={copyText} />);
    cy.get("button").click();
    cy.get("@writeTextStub").should("have.been.calledOnceWith", copyText);
  });
});
