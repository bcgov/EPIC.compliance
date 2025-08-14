import { MRT_ColumnDef, MRT_TableState } from "material-react-table";
import { useCallback } from "react";
import { Chip } from "@mui/material";
import { APPROVAL_STATUS } from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import PageLink from "@/components/Shared/PageLink";
import { InspectionGridQueryParams } from "@/models/Inspection";
import { ApprovalStatus } from "@/models/ApprovalStatus";
import { StaffUser } from "@/models/Staff";
import { Inspection } from "@/models/Inspection";
import { Initiation } from "@/models/Initiation";
import { IRProgress } from "@/models/IRProgress";
import { Project } from "@/models/Project";
import { IRStatus } from "@/models/IRStatus";

// Types for the data dependencies
export interface InspectionsGridDataDependencies {
  projectList?: Project[];
  initiationList?: Initiation[];
  irProgressList?: IRProgress[];
  approvalStatusList?: ApprovalStatus[];
  reviewerList?: StaffUser[];
  staffUserList?: StaffUser[];
  inspectionStatusList?: IRStatus[];
}

// Convert column filters to API query parameters
export const useConvertFiltersToQueryParams = (
  externalFilters: Record<string, string[] | string>
) => {
  return useCallback(
    (filters: MRT_TableState<Inspection>["columnFilters"]) => {
      const params: Partial<InspectionGridQueryParams> = {};

      filters.forEach((filter) => {
        switch (filter.id) {
          case "ir_number":
            if (typeof filter.value === "string" && filter.value.trim()) {
              params.ir_number = filter.value.trim();
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
          case "ir_progress":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.ir_progress = filter.value.join(",");
            }
            break;
          case "approval_status":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.approval_status = filter.value.join(",");
            }
            break;
          case "primary_officer":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.primary_officer_id = filter.value.join(",");
            }
            break;
          case "status":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.status = filter.value.join(",");
            }
            break;
          case "case_file_number":
            if (typeof filter.value === "string" && filter.value.trim()) {
              params.case_file_number = filter.value.trim();
            }
            break;
          case "start_date":
            if (typeof filter.value === "string" && filter.value.trim()) {
              // Convert the formatted date back to ISO format for the API
              const dateValue = filter.value.trim();
              if (dateValue) {
                // Assuming the date is in the format used by dateUtils.formatDate
                // You may need to adjust this based on your API expectations
                params.start_date = dateValue;
              }
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
            case "approval_status":
              params.approval_status = Array.isArray(value)
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
export const useInspectionsGridColumns = (
  dataDependencies: InspectionsGridDataDependencies
): MRT_ColumnDef<Inspection>[] => {
  const {
    projectList,
    initiationList,
    irProgressList,
    approvalStatusList,
    reviewerList,
    staffUserList,
    inspectionStatusList,
  } = dataDependencies;

  return [
    {
      accessorKey: "ir_number",
      header: "IR #",
      filterFn: "contains",
      Cell: ({ row }) => (
        <PageLink
          to="/ce-database/inspections/$inspectionNumber"
          params={{ inspectionNumber: row.original.ir_number }}
        />
      ),
    },
    {
      accessorFn: (row) => row.case_file?.project?.name,
      id: "project",
      header: "Project",
      filterVariant: "multi-select",
      filterSelectOptions:
        projectList?.map((project) => ({
          text: project.name,
          value: project.id.toString(),
        })) ?? [],
    },
    {
      accessorFn: (row) => dateUtils.formatDate(row.start_date),
      id: "start_date",
      header: "Start Date",
      filterVariant: "date",
      filterFn: "greaterThanOrEqual",
      size: 120,
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
      size: 120,
    },
    {
      accessorFn: (row) => row.ir_progress?.name,
      id: "ir_progress",
      header: "IR Progress",
      filterVariant: "multi-select",
      filterSelectOptions:
        irProgressList?.map((irProgress) => ({
          text: irProgress.name,
          value: irProgress.id.toString(),
        })) ?? [],
      size: 120,
    },
    {
      accessorFn: (row) => row.approval_status?.id,
      id: "approval_status",
      header: "Approval Status",
      Cell: ({ row }) => {
        return row.original.approval_status ? (
          <Chip
            label={row.original.approval_status?.name}
            color={
              row.original.approval_status?.id ===
              APPROVAL_STATUS.APPROVAL_PENDING
                ? "warning"
                : row.original.approval_status?.id === APPROVAL_STATUS.APPROVED
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
      filterSelectOptions:
        approvalStatusList?.map((approvalStatus) => ({
          text: approvalStatus.name,
          value: approvalStatus.id,
        })) ?? [],
      size: 100,
    },
    {
      accessorFn: (row) => row.approved_by?.name,
      id: "reviewer",
      header: "Reviewer",
      filterVariant: "multi-select",
      filterSelectOptions:
        reviewerList?.map((reviewer) => ({
          text: reviewer.name,
          value: reviewer.id.toString(),
        })) ?? [],
      size: 100,
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

    {
      accessorKey: "status",
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
      filterSelectOptions:
        inspectionStatusList?.map((inspectionStatus) => ({
          text: inspectionStatus.name,
          value: inspectionStatus.id.toString(),
        })) ?? [],
      size: 80,
    },
    {
      accessorFn: (row) => row.case_file?.case_file_number,
      id: "case_file_number",
      header: "Case File #",
      filterFn: "contains",
      Cell: ({ row }) => (
        <PageLink
          to="/ce-database/case-files/$caseFileNumber"
          params={{
            caseFileNumber: row.original.case_file?.case_file_number,
          }}
        />
      ),
    },
  ];
};
