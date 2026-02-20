/// <reference types="cypress" />
import {
  exportToCsv,
} from "@/components/Shared/MasterDataTable/utils";
import { MRT_RowData, MRT_TableInstance } from "material-react-table";


  describe("exportToCsv", () => {
    it("exports table data to CSV correctly", async () => {
      // Create a more complete mock of MRT_TableInstance
      const mockTable = {
        getVisibleFlatColumns: () => [
          { columnDef: { id: "name" } },
          { columnDef: { id: "age" } },
        ],
        getFilteredRowModel: () => ({
          flatRows: [
            {
              getValue: (column: string) => (column === "name" ? "John Doe" : 30),
            },
            {
              getValue: (column: string) => (column === "name" ? "Jane Smith" : 25),
            },
          ],
        }),
        // Adding a few more properties to avoid type errors
        getState: () => ({}),
        getAllColumns: () => [],
        getAllFlatColumns: () => [],
        getAllLeafColumns: () => [],
        getBottomRows: () => [],
        getCenterLeafColumns: () => [],
        getFlatHeaders: () => [],
        getHeaderGroups: () => [],
        getRowModel: () => ({ rows: [] }),
        getSortedRowModel: () => ({ rows: [] }),
        getPreFilteredRowModel: () => ({ rows: [] }),
      } as unknown as MRT_TableInstance<MRT_RowData>;
  
      // Spy on createObjectURL to ensure export is working
      cy.spy(window.URL, "createObjectURL").as("createObjectURL");
  
      await exportToCsv({
        table: mockTable,
        downloadDate: "2024-01-01",
        filenamePrefix: "staff",
      });
  
      // Validate that URL.createObjectURL was called, indicating CSV generation worked
      cy.get("@createObjectURL").should("be.calledOnce");
    });
  });
