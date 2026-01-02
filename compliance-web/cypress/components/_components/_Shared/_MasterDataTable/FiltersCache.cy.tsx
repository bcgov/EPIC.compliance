/* eslint-disable @typescript-eslint/no-explicit-any */
import { mount } from "cypress/react";
import { MRT_TableInstance } from "material-react-table";
import { FiltersCache } from "@/components/Shared/MasterDataTable/FiltersCache";

describe("FiltersCache Component", () => {
  it("does not call onCacheFilters on initial mount with filters", () => {
    const onCacheFilters = cy.stub().as("onCacheFiltersStub");

    const tableMock = {
      getState: () => ({
        columnFilters: [{ id: "name", value: "John" }],
      }),
    } as MRT_TableInstance<any>;

    mount(<FiltersCache onCacheFilters={onCacheFilters} table={tableMock} />);

    // Wait for the effect to run
    cy.wait(50);

    // Should NOT be called on initial mount since prevFilters equals currentFilters
    cy.get("@onCacheFiltersStub").should("not.have.been.called");
  });

  it("does not call onCacheFilters when filters are empty on mount", () => {
    const onCacheFilters = cy.stub().as("onCacheFiltersStub");

    const tableMock = {
      getState: () => ({
        columnFilters: [],
      }),
    } as MRT_TableInstance<any>;

    mount(<FiltersCache onCacheFilters={onCacheFilters} table={tableMock} />);
    cy.wait(50);
    // Should not be called when filters are empty
    cy.get("@onCacheFiltersStub").should("not.have.been.called");
  });
});
