import { useState } from "react";
import { mount } from "cypress/react";
import { ThemeProvider } from "@mui/material";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import type {
  MRT_ColumnDef,
  MRT_ColumnFiltersState,
} from "material-react-table";
import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import ClearAllFiltersButton from "@/components/Shared/MasterDataTable/ClearAllFiltersButton";
import { hasActiveFilters } from "@/components/Shared/MasterDataTable/filterUtils";
import { theme } from "@/styles/theme";

interface Row {
  id: number;
  title: string;
  status: string;
  date_created: string;
}

const rows: Row[] = [
  { id: 1, title: "Alpha", status: "Open", date_created: "2026-01-10" },
  { id: 2, title: "Beta", status: "Closed", date_created: "2026-02-10" },
];

const columns: MRT_ColumnDef<Row>[] = [
  { accessorKey: "id", header: "ID", enableColumnFilter: false },
  { accessorKey: "title", header: "Title", filterFn: "contains" },
  {
    accessorKey: "status",
    header: "Status",
    filterVariant: "multi-select",
    filterSelectOptions: [
      { text: "Open", value: "Open" },
      { text: "Closed", value: "Closed" },
    ],
  },
  {
    accessorKey: "date_created",
    header: "Date Created",
    filterVariant: "date",
    filterFn: "greaterThanOrEqual",
  },
];

const Grid = ({ initialFilters }: { initialFilters: MRT_ColumnFiltersState }) => {
  const [columnFilters, setColumnFilters] =
    useState<MRT_ColumnFiltersState>(initialFilters);

  return (
    <MasterDataTable
      columns={columns}
      data={rows}
      initialState={{ columnFilters }}
      state={{ columnFilters }}
      hideFilterToggle={true}
      renderTopToolbarCustomActions={() =>
        hasActiveFilters(columnFilters) ? (
          <ClearAllFiltersButton onClick={() => setColumnFilters([])} />
        ) : null
      }
      remoteDataConfig={{
        enableRemoteData: true,
        rowCount: rows.length,
        onColumnFiltersChange: setColumnFilters,
      }}
    />
  );
};

const mountGrid = (initialFilters: MRT_ColumnFiltersState) =>
  mount(
    <ThemeProvider theme={theme}>
      <LocalizationProvider dateAdapter={AdapterDayjs}>
        <Grid initialFilters={initialFilters} />
      </LocalizationProvider>
    </ThemeProvider>
  );

describe("Clear All filters", () => {
  it("is hidden when no filter is applied", () => {
    mountGrid([]);
    cy.contains("button", "Clear All").should("not.exist");
  });

  it("is hidden when filters were cleared back to empty values", () => {
    mountGrid([
      { id: "status", value: [] },
      { id: "date_created", value: "" },
    ]);
    cy.contains("button", "Clear All").should("not.exist");
  });

  it("shows for a default filter and clears every column filter input", () => {
    mountGrid([
      { id: "status", value: ["Open"] },
      { id: "date_created", value: "2026-01-01" },
    ]);

    cy.get('input[name="statusFilter"]').should("have.value", "Open");
    cy.get('input[placeholder="Date Created"]').should(
      "not.have.value",
      ""
    );

    cy.contains("button", "Clear All").click();

    cy.contains("button", "Clear All").should("not.exist");
    cy.get('input[name="statusFilter"]').should("have.value", "");
    cy.get('input[placeholder="Date Created"]').should("have.value", "");
  });

  it("shows for a text column filter and empties the text field", () => {
    mountGrid([]);
    cy.contains("button", "Clear All").should("not.exist");

    cy.get('input[placeholder="Title"]').type("Alp");
    cy.contains("button", "Clear All").should("be.visible").click();

    cy.contains("button", "Clear All").should("not.exist");
    cy.get('input[placeholder="Title"]').should("have.value", "");
  });

  it("shows once a column filter is applied in the table", () => {
    mountGrid([]);
    cy.contains("button", "Clear All").should("not.exist");

    cy.get('input[placeholder="Date Created"]').click();
    cy.get(".MuiPickersDay-root").not(".MuiPickersDay-hiddenDaySpacingFiller").first().click();

    cy.contains("button", "Clear All").should("be.visible").click();
    cy.contains("button", "Clear All").should("not.exist");
    cy.get('input[placeholder="Date Created"]').should("have.value", "");
  });
});
