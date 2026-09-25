/* eslint-disable @typescript-eslint/no-explicit-any */
/// <reference types="cypress" />
import MasterDataTable, { MaterialReactTableProps } from "@/components/Shared/MasterDataTable/MasterDataTable";
import { mount } from "cypress/react";
import { MRT_ColumnDef } from "material-react-table";

describe("MasterDataTable Component", () => {
  const columns: MRT_ColumnDef<any>[] = [
    {
      accessorKey: "name",
      header: "Name",
    },
    {
      accessorKey: "email",
      header: "Email",
    },
  ];

  const data = [
    { name: "John Doe", email: "john.doe@example.com" },
    { name: "Jane Doe", email: "jane.doe@example.com" },
  ];

  it("renders the MasterDataTable with the correct title and buttons", () => {
    const addRecordFunction = cy.stub().as("addRecordFunction");
    const tableProps: MaterialReactTableProps<any> = {
      columns,
      data,
      titleToolbarProps: {
        tableTitle: "User Data",
        tableAddRecordButtonText: "Add User",
        tableAddRecordFunction: addRecordFunction,
        tableAddRecordButtonVisibility: true,
      },
      enableExport: true,
      tableName: "UserTable",
    };

    mount(<MasterDataTable {...tableProps} />);

    cy.get("h5").should("contain.text", "User Data");
    cy.get("button").should("contain.text", "Add User");
    cy.get('button[id="addActionButton"]')
      .should("contain.text", "Add User")
      .click();
    cy.get("@addRecordFunction").should("have.been.calledOnce");
    cy.get('[aria-label="download"]').should("exist").click();
  });

  it("renders table rows and headers correctly", () => {
    const tableProps: MaterialReactTableProps<any> = {
      columns,
      data,
    };

    mount(<MasterDataTable {...tableProps} />);

    cy.get("th").contains("Name").should("exist");
    cy.get("th").contains("Email").should("exist");
    cy.get("td").contains("John Doe").should("exist");
    cy.get("td").contains("john.doe@example.com").should("exist");
  });

  it("renders NoDataComponent when data is empty", () => {
    const tableProps: MaterialReactTableProps<any> = {
      columns,
      data: [],
    };

    mount(<MasterDataTable {...tableProps} />);

    cy.get("h2").should("contain.text", "No results found");
  });

  it("calls setTableInstance with the table instance", () => {
    const setTableInstance = cy.stub().as("setTableInstanceStub");
    const tableProps: MaterialReactTableProps<any> = {
      columns,
      data,
      setTableInstance,
    };

    mount(<MasterDataTable {...tableProps} />);

    cy.get("@setTableInstanceStub").should("have.been.called");
  });

  it("checks export functionality", () => {
    const tableProps: MaterialReactTableProps<any> = {
      columns,
      data,
      enableExport: true,
      tableName: "UserTable",
    };

    cy.window().then((win) => {
      cy.stub(win.URL, "createObjectURL").returns("blob-url");
    });

    mount(<MasterDataTable {...tableProps} />);

    cy.get('[aria-label="download"]').click();

    // Assert that the export function was called
    cy.get("a[download]")
      .should("exist")
      .and("have.attr", "href")
      .and("match", /^blob:/);
  });
});

describe("MasterDataTable horizontal scrolling", () => {
  const wideColumns: MRT_ColumnDef<any>[] = ["a", "b", "c", "d"].map(
    (key) => ({ accessorKey: key, header: key.toUpperCase(), size: 600 })
  );
  const manyRows = Array.from({ length: 50 }, (_, i) => ({
    a: `a${i}`,
    b: `b${i}`,
    c: `c${i}`,
    d: `d${i}`,
  }));

  // Mirrors the page layout in routes/__root.tsx: a height-bounded flex
  // column that scrolls its own overflow.
  const mountInPageLayout = (
    data: any[],
    props: Partial<MaterialReactTableProps<any>> = {},
    pageHeight = 800
  ) =>
    mount(
      <div
        data-testid="page"
        style={{
          display: "flex",
          flexDirection: "column",
          height: `${pageHeight}px`,
          width: "1000px",
          overflow: "auto",
        }}
      >
        <MasterDataTable columns={wideColumns} data={data} {...props} />
      </div>
    );

  const assertScrollbarVisible = () => {
    cy.get(".MuiTableContainer-root").then(($container) => {
      const container = $container[0];
      expect(container.scrollWidth).to.be.greaterThan(container.clientWidth);
      const page = Cypress.$('[data-testid="page"]')[0];
      // The container's bottom edge (where the horizontal scrollbar lives)
      // must be inside the visible page area, not scrolled out of view.
      expect(container.getBoundingClientRect().bottom).to.be.at.most(
        page.getBoundingClientRect().bottom
      );
    });
  };

  it("keeps the horizontal scrollbar in view when the grid has rows", () => {
    mountInPageLayout(manyRows);
    cy.get("td").contains("a0").should("exist");
    assertScrollbarVisible();
  });

  it("keeps the horizontal scrollbar in view when the grid is empty", () => {
    mountInPageLayout([]);
    cy.get("h2").should("contain.text", "No results found");
    assertScrollbarVisible();
  });

  it("does not clip a tall custom toolbar when space is tight", () => {
    mountInPageLayout(
      manyRows,
      {
        renderTopToolbarCustomActions: () => (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <h5 style={{ margin: 0, height: 40 }}>Title</h5>
            <button data-testid="toolbar-second-row" style={{ height: 40 }}>
              Export
            </button>
          </div>
        ),
      },
      500
    );
    cy.get("td").contains("a0").should("exist");
    cy.get(".MuiPaper-root").then(($paper) => {
      const topToolbar = $paper[0].children[0] as HTMLElement;
      // MRT toolbars are overflow: hidden, so any shrinking clips content.
      expect(topToolbar.clientHeight).to.equal(topToolbar.scrollHeight);
    });
    assertScrollbarVisible();
  });
});
