import { MRT_ColumnDef, MRT_TableState } from "material-react-table";
import { useCallback } from "react";
import { Chip } from "@mui/material";
import dateUtils from "@/utils/dateUtils";
import PageLink from "@/components/Shared/PageLink";
import { CaseFile, CaseFileGridQueryParams } from "@/models/CaseFile";
import { Project } from "@/models/Project";
import { Initiation } from "@/models/Initiation";
import { StaffUser } from "@/models/Staff";

// Types for the data dependencies
export interface CaseFileGridDataDependencies {
  projectList?: Project[];
  initiationList?: Initiation[];
  staffUserList?: StaffUser[];
}

// Convert column filters to API query parameters
export const useConvertFiltersToQueryParams = (
  externalFilters: Record<string, string[] | string>
) => {
  return useCallback(
    (filters: MRT_TableState<CaseFile>["columnFilters"]) => {
      const params: Partial<CaseFileGridQueryParams> = {};

      filters.forEach((filter) => {
        switch (filter.id) {
          case "case_file_number":
            if (typeof filter.value === "string" && filter.value.trim()) {
              params.case_file_number = filter.value.trim();
            }
            break;
          case "project":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.project_id = filter.value.join(",");
            }
            break;
          case "initiation":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.initiation_id = filter.value.join(",");
            }
            break;
          case "date_created":
            if (typeof filter.value === "string" && filter.value.trim()) {
              const dateValue = filter.value.trim();
              if (dateValue) {
                params.date_created = dateValue;
              }
            }
            break;
          case "status":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.status = filter.value.join(",");
            }
            break;
          case "primary_officer":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.primary_officer_id = filter.value.join(",");
            }
            break;
        }
      });

      // Add external filters
      Object.entries(externalFilters).forEach(([key, value]) => {
        if (value && (Array.isArray(value) ? value.length > 0 : value !== "")) {
          switch (key) {
            case "primary_officer_id":
              params.primary_officer_id = Array.isArray(value)
                ? value.join(",")
                : value;
              break;
            case "project_id":
              params.project_id = Array.isArray(value)
                ? value.join(",")
                : value;
              break;
          }
        }
      });

      return params;
    },
    [externalFilters]
  );
};

// Create columns configuration
export const useCaseFileGridColumns = (
  dataDependencies: CaseFileGridDataDependencies
): MRT_ColumnDef<CaseFile>[] => {
  const { projectList, initiationList, staffUserList } = dataDependencies;

  const statusOptions = [
    { text: "Open", value: "Open" },
    { text: "Closed", value: "Closed" },
  ];

  return [
    {
      accessorKey: "case_file_number",
      header: "Case File #",
      filterFn: "contains",
      Cell: ({ row }) => (
        <PageLink
          to="/ce-database/case-files/$caseFileNumber"
          params={{ caseFileNumber: row.original.case_file_number }}
        />
      ),
      size: 120,
    },
    {
      accessorFn: (row) => row.project?.name,
      id: "project",
      header: "Project",
      filterVariant: "multi-select",
      filterSelectOptions:
        projectList?.map((project) => ({
          text: project.name,
          value: project.id.toString(),
        })) ?? [],
      size: 150,
    },
    {
      accessorFn: (row) => row.initiation?.name,
      id: "initiation",
      header: "Initiation",
      filterVariant: "multi-select",
      filterSelectOptions:
        initiationList?.map((initiation) => ({
          text: initiation.name,
          value: initiation.id.toString(),
        })) ?? [],
      size: 150,
    },
    {
      accessorFn: (row) =>
        row.date_created ? dateUtils.formatDate(row.date_created) : "",
      id: "date_created",
      header: "Date Created",
      filterVariant: "date",
      filterFn: "greaterThanOrEqual",
      size: 120,
    },
    {
      accessorKey: "status",
      header: "Status",
      Cell: ({ row }) => {
        return row.original.case_file_status ? (
          <Chip
            label={row.original.case_file_status}
            color={
              row.original.case_file_status?.toLowerCase() === "open"
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
      filterSelectOptions: statusOptions,
      size: 80,
    },
    {
      accessorFn: (row) => row.primary_officer?.name,
      id: "primary_officer",
      header: "Primary",
      filterVariant: "multi-select",
      filterSelectOptions:
        staffUserList?.map((staffUser) => ({
          text: staffUser.name,
          value: staffUser.id.toString(),
        })) ?? [],
      size: 100,
    },
  ];
};
