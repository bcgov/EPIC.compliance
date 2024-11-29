import TableFilter from "@/components/Shared/FilterSelect/TableFilter";
import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import { searchFilter } from "@/components/Shared/MasterDataTable/utils";
import PageLink from "@/components/Shared/PageLink";
import { useInspectionsData } from "@/hooks/useInspections";
import { Inspection } from "@/models/Inspection";
import { Chip } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { MRT_ColumnDef } from "material-react-table";
import { useMemo, useCallback } from "react";

export const Route = createFileRoute(
  "/_authenticated/ce-database/inspections/"
)({ component: Inspections });

export function Inspections() {
  const { data: inspectionsList, isLoading } = useInspectionsData();

  const createUniqueFilterList = useCallback(
    (key: keyof Inspection, subKey?: string): string[] => {
      return [
        ...new Set(
          inspectionsList?.map((item) => {
            const value = item[key];
            if (typeof value === "object" && value !== null) {
              if (subKey && subKey in value) {
                return (value as unknown as Record<string, unknown>)[
                  subKey
                ] as string;
              }
              return "";
            }
            return typeof value === "string" ? value : "";
          })
        ),
      ].filter(Boolean) as string[];
    },
    [inspectionsList]
  );

  const projectList = useMemo(
    () =>
      [
        ...new Set(
          inspectionsList?.map((ins) => ins.case_file?.project?.name ?? "")
        ),
      ].filter(Boolean),
    [inspectionsList]
  );
  const initiationList = useMemo(
    () => createUniqueFilterList("initiation", "name"),
    [createUniqueFilterList]
  );
  const staffUserList = useMemo(
    () => createUniqueFilterList("primary_officer", "name"),
    [createUniqueFilterList]
  );
  const irStatusList = useMemo(
    () => createUniqueFilterList("ir_status", "name"),
    [createUniqueFilterList]
  );
  const irTypeList = useMemo(
    () => createUniqueFilterList("types_text"),
    [createUniqueFilterList]
  );
  const inspectionStatusList = useMemo(
    () => createUniqueFilterList("inspection_status"),
    [createUniqueFilterList]
  );

  const columns = useMemo<MRT_ColumnDef<Inspection>[]>(
    () => [
      {
        accessorKey: "ir_number",
        header: "IR #",
        sortingFn: "sortFn",
        filterFn: searchFilter,
        Cell: ({ row }) => (
          <PageLink
            to="/ce-database/inspections/$inspectionNumber"
            params={{ inspectionNumber: row.original.ir_number }}
          />
        ),
      },
      {
        accessorFn: (row) => row.case_file?.project?.name,
        header: "Project",
        filterVariant: "multi-select",
        filterSelectOptions: projectList,
        Filter: ({ header, column }) => (
          <TableFilter
            isMulti
            header={header}
            column={column}
            variant="inline"
            name="projectFilter"
            placeholder="Filter"
          />
        ),
      },
      {
        accessorKey: "ir_status.name",
        header: "Stage",
        filterVariant: "multi-select",
        filterSelectOptions: irStatusList,
        Filter: ({ header, column }) => (
          <TableFilter
            isMulti
            header={header}
            column={column}
            variant="inline"
            name="stageFilter"
            placeholder="Filter"
          />
        ),
        size: 120,
      },
      {
        accessorKey: "types_text",
        header: "Type",
        filterVariant: "multi-select",
        filterSelectOptions: irTypeList,
        Filter: ({ header, column }) => (
          <TableFilter
            isMulti
            header={header}
            column={column}
            variant="inline"
            name="typeFilter"
            placeholder="Filter"
          />
        ),
        size: 120,
      },
      {
        accessorKey: "initiation.name",
        header: "Initiation",
        filterVariant: "multi-select",
        filterSelectOptions: initiationList,
        Filter: ({ header, column }) => (
          <TableFilter
            isMulti
            header={header}
            column={column}
            variant="inline"
            name="initiationFilter"
            placeholder="Filter"
          />
        ),
      },
      {
        accessorKey: "inspection_status",
        header: "Status",
        Cell: ({ row }) => {
          return row.original.inspection_status ? (
            <Chip
              label={row.original.inspection_status}
              color={
                row.original.inspection_status?.toLowerCase() === "open"
                  ? "success"
                  : "error"
              }
              variant="outlined"
              size="small"
            />
          ) : (
            <></>
          );
        },
        filterVariant: "multi-select",
        filterSelectOptions: inspectionStatusList,
        Filter: ({ header, column }) => (
          <TableFilter
            isMulti
            header={header}
            column={column}
            variant="inline"
            name="inspectionStatusFilter"
            placeholder="Filter"
          />
        ),
        size: 120,
      },
      {
        accessorFn: (row) => row.primary_officer?.name,
        id: "primary_officer.name",
        header: "Primary",
        filterVariant: "multi-select",
        filterSelectOptions: staffUserList,
        Filter: ({ header, column }) => (
          <TableFilter
            isMulti
            header={header}
            column={column}
            variant="inline"
            name="primaryOfficerFilter"
            placeholder="Filter"
          />
        ),
      },
      {
        accessorKey: "case_file.case_file_number",
        header: "Case File #",
        filterFn: searchFilter,
        Cell: ({ row }) => (
          <PageLink
            to="/ce-database/case-files/$caseFileNumber"
            params={{
              caseFileNumber: row.original.case_file?.case_file_number,
            }}
          />
        ),
      },
    ],
    [
      projectList,
      initiationList,
      staffUserList,
      irStatusList,
      irTypeList,
      inspectionStatusList,
    ]
  );

  return (
    <MasterDataTable
      columns={columns}
      data={inspectionsList ?? []}
      initialState={{
        sorting: [{ id: "ir_number", desc: false }],
      }}
      state={{
        isLoading,
        showGlobalFilter: true,
      }}
      titleToolbarProps={{
        tableTitle: "Inspections",
      }}
    />
  );
}
