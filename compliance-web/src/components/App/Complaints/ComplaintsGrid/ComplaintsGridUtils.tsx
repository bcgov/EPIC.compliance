import { MRT_ColumnDef, MRT_TableState } from "material-react-table";
import { useCallback } from "react";
import { Chip } from "@mui/material";
import dateUtils from "@/utils/dateUtils";
import PageLink from "@/components/Shared/PageLink";
import { Complaint, ComplaintGridQueryParams } from "@/models/Complaint";
import { Project } from "@/models/Project";
import { Topic } from "@/models/Topic";
import { ComplaintSource } from "@/models/ComplaintSource";
import { StaffUser } from "@/models/Staff";
import { ComplaintStatusEnum } from "@/utils/constants";

// Types for the data dependencies
export interface ComplaintsGridDataDependencies {
  projectList?: Project[];
  topicList?: Topic[];
  complaintSourceList?: ComplaintSource[];
  staffUserList?: StaffUser[];
}

// Convert column filters to API query parameters
export const useConvertFiltersToQueryParams = (
  externalFilters: Record<string, string[] | string>
) => {
  return useCallback(
    (filters: MRT_TableState<Complaint>["columnFilters"]) => {
      const params: Partial<ComplaintGridQueryParams> = {};

      filters.forEach((filter) => {
        switch (filter.id) {
          case "complaint_number":
            if (typeof filter.value === "string" && filter.value.trim()) {
              params.complaint_number = filter.value.trim();
            }
            break;
          case "project":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.project_ids = filter.value.join(",");
            }
            break;
          case "topic_id":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.topic_ids = filter.value.join(",");
            }
            break;
          case "date_received":
            if (typeof filter.value === "string" && filter.value.trim()) {
              const dateValue = filter.value.trim();
              if (dateValue) {
                params.date_received = dateValue;
              }
            }
            break;
          case "source_type_id":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.source_type_ids = filter.value.join(",");
            }
            break;
          case "primary_officer_id":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.primary_officer_ids = filter.value.join(",");
            }
            break;
          case "status":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.statuses = filter.value.join(",");
            }
            break;
          case "case_file_number":
            if (typeof filter.value === "string" && filter.value.trim()) {
              params.case_file_number = filter.value.trim();
            }
            break;
        }
      });

      // Add external filters
      Object.entries(externalFilters).forEach(([key, value]) => {
        if (value && (Array.isArray(value) ? value.length > 0 : value !== "")) {
          switch (key) {
            case "primary_officer_ids":
              params.primary_officer_ids = Array.isArray(value)
                ? value.join(",")
                : value;
              break;
            case "project_ids":
              params.project_ids = Array.isArray(value)
                ? value.join(",")
                : value;
              break;
            case "statuses":
              params.statuses = Array.isArray(value)
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
export const useComplaintsGridColumns = (
  dataDependencies: ComplaintsGridDataDependencies
): MRT_ColumnDef<Complaint>[] => {
  const {
    projectList,
    topicList,
    complaintSourceList,
    staffUserList,
  } = dataDependencies;

  const statusOptions = [
    { text: "Open", value: ComplaintStatusEnum.OPEN },
    { text: "Closed", value: ComplaintStatusEnum.CLOSED },
  ];

  return [
    {
      accessorKey: "complaint_number",
      header: "Complaint #",
      filterFn: "contains",
      Cell: ({ row }) => (
        <PageLink
          to="/ce-database/complaints/$complaintNumber"
          params={{ complaintNumber: row.original.complaint_number }}
        />
      ),
      size: 120,
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
      size: 150,
    },
    {
      accessorFn: (row) => row.topic?.name,
      id: "topic_id",
      header: "Topic",
      filterVariant: "multi-select",
      filterSelectOptions:
        topicList?.map((topic) => ({
          text: topic.name,
          value: topic.id.toString(),
        })) ?? [],
      size: 150,
    },
    {
      accessorFn: (row) =>
        row.date_received ? dateUtils.formatDate(row.date_received) : "",
      id: "date_received",
      header: "Date Received",
      filterVariant: "date",
      filterFn: "greaterThanOrEqual",
      size: 120,
    },
    {
      accessorFn: (row) => row.source_type?.name,
      id: "source_type_id",
      header: "Complaint Source",
      filterVariant: "multi-select",
      filterSelectOptions:
        complaintSourceList?.map((source) => ({
          text: source.name,
          value: source.id.toString(),
        })) ?? [],
      size: 150,
    },
    {
      accessorFn: (row) => row.primary_officer?.name,
      id: "primary_officer_id",
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
        return row.original.status ? (
          <Chip
            label={row.original.status}
            color={
              row.original.status === ComplaintStatusEnum.OPEN
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
      size: 120,
    },
  ];
}; 
