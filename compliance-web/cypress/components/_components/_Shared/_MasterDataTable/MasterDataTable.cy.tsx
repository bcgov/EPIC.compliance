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
