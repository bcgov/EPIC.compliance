import LexicalEditor from "@/components/Shared/LexicalEditor/LexicalEditor";
import { mount } from "cypress/react";
import { MentionData } from "@/components/Shared/LexicalEditor/LexicalUtils";

describe("LexicalEditor Component", () => {
  const defaultProps = {
    placeholder: "Enter text here...",
  };

  function mountLexicalEditor(props) {
    const onChangeStub = cy.stub().as("onChangeHandler");
    mount(
      <LexicalEditor {...defaultProps} {...props} onChange={onChangeStub} />
    );
  }

  it("renders with basic props", () => {
    mountLexicalEditor({});

    cy.get(".editor-container").should("exist");
    cy.get(".editor-placeholder").should("contain", "Enter text here...");
  });

  it("renders with a label", () => {
    mountLexicalEditor({ label: "Test Label" });

    cy.get("label").should("contain", "Test Label");
  });

  it("shows error state when errorMsg is provided", () => {
    mountLexicalEditor({ errorMsg: "This is an error" });

    cy.get(".editor-container").should(
      "have.css",
      "border-color",
      "rgb(206, 62, 57)"
    );
  });

  it("renders with default HTML content", () => {
    mountLexicalEditor({ defaultHtml: "<p>Default content</p>" });

    cy.get(".editor-input").should("contain", "Default content");
  });

  it("renders advanced toolbar when isAdvanced is true", () => {
    mountLexicalEditor({ isAdvanced: true });

    cy.get('button[aria-label="Table"]').should("exist");
    cy.get('button[aria-label="Text Alignment"]').should("exist");
  });

  it("renders table when table button is clicked", () => {
    mountLexicalEditor({ isAdvanced: true });

    cy.get('button[aria-label="Table"]').should("exist").click();
    cy.get('table[class="editor-table"]').should("exist");
    cy.get(".editor-tableCell").first().click();
    cy.get('button[aria-label="cell-action-menu"]').should("exist").click();

    cy.get('li[data-test-id="table-insert-row-above"').should("exist").click();
  });

  it("renders with custom height", () => {
    mountLexicalEditor({ height: "300px" });

    cy.get(".editor-container").should("have.css", "height", "300px");
  });

  it("allows typing text", () => {
    mountLexicalEditor({});

    cy.get(".editor-input")
      .click()
      .type("Hello, World!")
      .should("contain", "Hello, World!");
  });

  it("renders with mentions list when provided", () => {
    const mentionsList: MentionData[] = [
      { id: 1, name: "John Doe" },
      { id: 2, name: "Jane Smith" },
    ];

    mountLexicalEditor({ mentionsList });

    cy.get(".editor-input").click().type("@J");

    cy.get(".mentions-menu").should("exist");
    cy.get(".mentions-menu").should("contain", "John Doe");
    cy.get(".mentions-menu").should("contain", "Jane Smith");
  });
});

// describe("LexicalEditor Component - Advanced Table", () => {
//   const defaultProps = {
//     placeholder: "Enter text here...",
//   };

//   function mountLexicalEditor(props) {
//     const onChangeStub = cy.stub().as("onChangeHandler");
//     mount(
//       <LexicalEditor {...defaultProps} {...props} onChange={onChangeStub} />
//     );
//   }

//   beforeEach(() => {
//     cy.viewport(1280, 720);
//     mountLexicalEditor({ isAdvanced: true });
//     cy.get('button[aria-label="Table"]').should("exist").click();
//   });

//   const doTableCellClick = (isLastCell = false) => {
//     if (isLastCell) {
//       cy.get(".editor-tableCell").last().click();
//     } else {
//       cy.get(".editor-tableCell").first().click();
//     }
//     cy.get('button[aria-label="cell-action-menu"]').should("exist").click();
//   };

//   it("renders table with default content", () => {
//     cy.get('table[class="editor-table"]').should("exist");
//   });

//   it("toggle row striping", () => {
//     doTableCellClick();
//     cy.get('li[data-test-id="table-row-striping"').should("exist").click();
//   });

//   it("inserts row above", () => {
//     doTableCellClick();
//     cy.get('li[data-test-id="table-insert-row-above"').should("exist").click();
//   });

//   it("inserts row below", () => {
//     doTableCellClick();
//     cy.get('li[data-test-id="table-insert-row-below"').should("exist").click();
//   });

//   it("inserts column left", () => {
//     doTableCellClick();
//     cy.get('li[data-test-id="table-insert-column-before"')
//       .should("exist")
//       .click();
//   });

//   it("inserts column right", () => {
//     doTableCellClick();

//     // Break up the chain as suggested by the Cypress error message
//     cy.get('li[data-test-id="table-insert-column-after"').as('insertColumnBtn');
//     cy.get('@insertColumnBtn').should("exist");
//     cy.get('@insertColumnBtn').click();
//   });

//   // it("deletes column", () => {
//   //   doTableCellClick();
//   //   cy.get('li[data-test-id="table-delete-columns"').should("exist").click();
//   // });

//   it("deletes row", () => {
//     doTableCellClick();
//     cy.get('li[data-test-id="table-delete-rows"').should("exist").click();
//   });

//   it("deletes table", () => {
//     doTableCellClick();
//     cy.get('li[data-test-id="table-delete"').should("exist").click();
//   });

//   it("removes row header if cell is header", () => {
//     doTableCellClick();
//     cy.contains("li", "Remove row header").should("exist");
//     cy.get('li[data-test-id="table-row-header"').should("exist").click();
//   });

//   it("removes column header if cell is header", () => {
//     doTableCellClick();
//     cy.contains("li", "Remove column header").should("exist");
//     cy.get('li[data-test-id="table-column-header"').should("exist").click();
//   });

//   it("adds row header if cell is not header", () => {
//     doTableCellClick(true);
//     cy.contains("li", "Add row header").should("exist");
//     cy.get('li[data-test-id="table-row-header"').should("exist").click();
//   });

//   it("adds column header if cell is not header", () => {
//     doTableCellClick(true);
//     cy.contains("li", "Add column header").should("exist");
//     cy.get('li[data-test-id="table-column-header"').should("exist").click();
//   });
// });

// describe("LexicalEditor Component - Table Hover Actions", () => {
//   const defaultProps = {
//     placeholder: "Enter text here...",
//   };

//   function mountLexicalEditor(props) {
//     const onChangeStub = cy.stub().as("onChangeHandler");
//     mount(
//       <LexicalEditor {...defaultProps} {...props} onChange={onChangeStub} />
//     );
//   }

//   beforeEach(() => {
//     cy.viewport(1280, 720);
//     mountLexicalEditor({ isAdvanced: true });
//     cy.get('button[aria-label="Table"]').should("exist").click();
//   });

//   // it("should show add row button when hovering last cell of a row", () => {
//   //   cy.wait(500);
//   //   cy.get(".editor-tableCell").last().scrollIntoView().trigger("mousemove", { force: true });
//   //   cy.get(".editor-tableAddRows", { timeout: 10000 })
//   //     .should("exist")
//   //     .should("have.css", "visibility", "visible");
//   // });

//   it("should add new row when clicking add row button", () => {
//     cy.wait(500);
//     cy.get(".editor-tableCell").last().scrollIntoView().trigger("mousemove", { force: true });
//     cy.get(".editor-tableAddRows", { timeout: 10000 })
//       .should("exist")
//       .should("have.css", "visibility", "visible")
//       .click({ force: true });
//     cy.get(".editor-table tr").should("have.length", 4);
//   });
// });

// describe("LexicalEditor Component - Table Cell Resizer", () => {
//   const defaultProps = {
//     placeholder: "Enter text here...",
//   };

//   function mountLexicalEditor(props) {
//     const onChangeStub = cy.stub().as("onChangeHandler");
//     mount(
//       <LexicalEditor {...defaultProps} {...props} onChange={onChangeStub} />
//     );
//   }

//   beforeEach(() => {
//     cy.viewport(1280, 720);
//     mountLexicalEditor({ isAdvanced: true });
//     cy.get('button[aria-label="Table"]').should("exist").click();
//   });

//   // it("should show column resizer when hovering over the right edge of a cell", () => {
//   //   cy.wait(500);
//   //   cy.get(".editor-tableCell").first().scrollIntoView().trigger("mousemove", { force: true });
//   //   cy.get(".TableCellResizer__resizer", { timeout: 10000 })
//   //     .should("exist")
//   //     .should("have.css", "cursor", "col-resize");
//   // });

//   it("should show row resizer when hovering over the bottom edge of a cell", () => {
//     cy.wait(500);
//     cy.get(".editor-tableCell").first().scrollIntoView().trigger("mousemove", { force: true });
//     cy.get(".TableCellResizer__resizer", { timeout: 10000 })
//       .last()
//       .should("exist")
//       .should("have.css", "cursor", "row-resize");
//   });

//   it("should resize column width when dragging column resizer", () => {
//     cy.wait(500);
//     cy.get(".editor-tableCell").first().scrollIntoView().trigger("mousemove", { force: true });

//     cy.get(".TableCellResizer__resizer")
//       .first()
//       .should('be.visible')
//       .trigger("mousedown", { which: 1, force: true })
//       .trigger("mousemove", { clientX: 200, force: true })
//       .trigger("mouseup", { force: true });

//     cy.get(".editor-tableCell").first().invoke('outerWidth').should('be.gt', 50);
//   });

//   it("should resize row height when dragging row resizer", () => {
//     cy.wait(500);
//     cy.get(".editor-tableCell").first().scrollIntoView().trigger("mousemove", { force: true });

//     cy.get(".TableCellResizer__resizer")
//       .last()
//       .should('be.visible')
//       .trigger("mousedown", { which: 1, force: true })
//       .trigger("mousemove", { clientY: 200, force: true })
//       .trigger("mouseup", { force: true });

//     cy.get(".editor-tableCell").first().invoke('height').should('be.gt', 20);
//   });
// });

