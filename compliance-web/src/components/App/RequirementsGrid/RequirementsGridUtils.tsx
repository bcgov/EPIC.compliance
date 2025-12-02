import { MRT_ColumnDef, MRT_TableState } from "material-react-table";
import { useCallback } from "react";
import {
  APPROVAL_STATUS,
  APReferralStatus,
  CRStatus,
  EnforcementActionEnum,
  OrderProgressEnum,
  OrderStatusEnum,
  ViolationTicketStatus,
  WarningLetterProgressEnum,
} from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import PageLink from "@/components/Shared/PageLink";
import {
  InspectionRequirementGrid,
  InspectionRequirementGridQueryParams,
} from "@/models/InspectionRequirementGrid";
import { Topic } from "@/models/Topic";
import { ComplianceFinding } from "@/models/ComplianceFinding";
import { EnforcementAction } from "@/models/EnforcementAction";
import { RequirementSource } from "@/models/RequirementSource";
import { InspectionMoreDetailsEnforcementAction } from "@/models/Inspection";
import EnforcementStatusFlag from "@/components/App/Inspections/Profile/Enforcements/EnforcementStatusFlag";

// Types for the data dependencies
export interface RequirementsGridDataDependencies {
  topics?: Topic[];
  complianceFindings?: ComplianceFinding[];
  enforcementActions?: EnforcementAction[];
  requirementSources?: RequirementSource[];
}

// Convert column filters to API query parameters
export const useConvertFiltersToQueryParams = (
  externalFilters: Record<string, string[] | string>
) => {
  return useCallback(
    (filters: MRT_TableState<InspectionRequirementGrid>["columnFilters"]) => {
      const params: Partial<InspectionRequirementGridQueryParams> = {};

      filters.forEach((filter) => {
        switch (filter.id) {
          case "tpc":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.tpc_ids = filter.value.join(",");
            }
            break;
          case "summary":
            if (typeof filter.value === "string" && filter.value.trim()) {
              params.summary = filter.value.trim();
            }
            break;
          case "cmd_fnd":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.cmd_fnd_ids = filter.value.join(",");
            }
            break;
          case "enf_actn":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.enf_actn_ids = filter.value.join(",");
            }
            break;
          case "enf_stats":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.enf_stats = filter.value.join(",");
            }
            break;
          case "enf_number":
            if (typeof filter.value === "string" && filter.value.trim()) {
              params.enf_number = filter.value.trim();
            }
            break;
          case "req_src_num":
            if (typeof filter.value === "string" && filter.value.trim()) {
              params.req_src_num = filter.value.trim();
            }
            break;
          case "req_src":
            if (Array.isArray(filter.value) && filter.value.length > 0) {
              params.req_src_ids = filter.value.join(",");
            }
            break;
          case "ir_no":
            if (typeof filter.value === "string" && filter.value.trim()) {
              params.ir_no = filter.value.trim();
            }
            break;
          case "date_issued":
            if (typeof filter.value === "string" && filter.value.trim()) {
              // Convert the formatted date back to ISO format for the API
              const dateValue = filter.value.trim();
              if (dateValue) {
                // Assuming the date is in the format used by dateUtils.formatDate
                // You may need to adjust this based on your API expectations
                params.date_issued = dateValue;
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
              params.prm_offc_ids = Array.isArray(value)
                ? value.join(",")
                : value;
              break;
            case "enf_stats":
              params.enf_stats = Array.isArray(value) ? value.join(",") : value;
              break;
            case "inspection_status":
              params.insp_sts = Array.isArray(value) ? value.join(",") : value;
              break;
            case "project_id":
              params.project_ids = Array.isArray(value)
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
export const useRequirementsGridColumns = (
  dataDependencies: RequirementsGridDataDependencies
): MRT_ColumnDef<InspectionRequirementGrid>[] => {
  const RequirementSourceNames = {
    SCHEDULE_B: "Schedule B - Table of Conditions",
    SCHEDULE_A: "Schedule A - Certified Project Description",
  };

  const RequirementSourceNameMap: Record<string, string> = {
    [RequirementSourceNames.SCHEDULE_B]: "Schedule B",
    [RequirementSourceNames.SCHEDULE_A]: "Schedule A",
  };

  const { topics, complianceFindings, enforcementActions, requirementSources } =
    dataDependencies;

  return [
    {
      accessorFn: (row) => row.topic?.name,
      id: "tpc",
      header: "Topic",
      filterVariant: "multi-select",
      filterSelectOptions:
        topics?.map((topic) => ({
          text: topic.name,
          value: topic.id.toString(),
        })) ?? [],
      size: 120,
    },
    {
      accessorKey: "summary",
      header: "Requirement Summary",
      filterFn: "contains",
      size: 200,
    },
    {
      accessorFn: (row) => row.compliance_finding?.name,
      id: "cmd_fnd",
      header: "Compliance Finding",
      filterVariant: "multi-select",
      filterSelectOptions:
        complianceFindings?.map((complianceFinding) => ({
          text: complianceFinding.name,
          value: complianceFinding.id.toString(),
        })) ?? [],
      size: 80,
    },
    {
      accessorFn: (row) => row.enforcement_action?.name,
      id: "enf_actn",
      header: "Enforcement Action",
      filterVariant: "multi-select",
      filterSelectOptions:
        enforcementActions?.map((enforcementAction) => ({
          text: enforcementAction.name,
          value: enforcementAction.id.toString(),
        })) ?? [],
      size: 150,
    },
    {
      accessorKey: "enf_stats",
      header: "Enf. Status",
      Cell: ({ row }) => {
        const enforcementStatusFlagObj: InspectionMoreDetailsEnforcementAction =
          {
            id: row.original.enforcement_action.id,
            name: row.original.enforcement_action.name,
            progress: row.original.progress,
            status: row.original.status,
          };
        return (
          <EnforcementStatusFlag
            enforcementActionType={
              row.original.enforcement_action.id as EnforcementActionEnum
            }
            enforcementActionDetails={enforcementStatusFlagObj}
          />
        );
      },
      filterVariant: "multi-select",
      filterSelectOptions: enforcementStatusOptions,
      size: 120,
    },
    {
      accessorFn: (row) => row.enforcement_number,
      id: "enf_number",
      header: "Enf. Document #",
      filterFn: "contains",
      enableSorting: true,
      sortingFn: "alphanumeric",
      sortDescFirst: false,
      size: 80,
    },
    {
      accessorFn: (row) => row.requirement_number,
      id: "req_src_num",
      header: "Condition #",
      filterFn: "contains",
      enableSorting: true,
      sortingFn: "alphanumeric",
      sortDescFirst: false,
      size: 80,
    },
    {
      accessorFn: (row) => {
        return (
          row.requirement_sources
            ?.map((source) => {
              if (source.name === RequirementSourceNames.SCHEDULE_B) {
                return RequirementSourceNameMap[
                  RequirementSourceNames.SCHEDULE_B
                ];
              }
              if (source.name === RequirementSourceNames.SCHEDULE_A) {
                return RequirementSourceNameMap[
                  RequirementSourceNames.SCHEDULE_A
                ];
              }
              return source.name;
            })
            .join(", ") ?? ""
        );
      },
      id: "req_src",
      header: "Source",
      filterVariant: "multi-select",
      filterSelectOptions:
        requirementSources?.map((requirementSource) => ({
          text: requirementSource.name,
          value: requirementSource.id.toString(),
        })) ?? [],
      size: 100,
    },
    {
      accessorKey: "ir_no",
      header: "IR #",
      filterFn: "contains",
      Cell: ({ row }) => (
        <PageLink
          to="/ce-database/inspections/$inspectionNumber"
          params={{ inspectionNumber: row.original.ir_number }}
        />
      ),
      size: 120,
    },
    {
      accessorFn: (row) =>
        row.date_issued ? dateUtils.formatDate(row.date_issued) : "",
      id: "date_issued",
      header: "IR Issuance Date",
      filterVariant: "date",
      filterFn: "greaterThanOrEqual",
      size: 120,
    },
  ];
};

export const enforcementStatusOptions = [
  // Order Statuses
  {
    value: OrderProgressEnum.DRAFTING,
    text: "Drafting",
  },
  {
    value: OrderStatusEnum.OPEN,
    text: "Open",
  },
  {
    value: OrderStatusEnum.CLOSED,
    text: "Closed",
  },
  {
    value: OrderStatusEnum.RESCINDED,
    text: "Rescinded",
  },
  {
    value: OrderProgressEnum.DEPUTY_REVIEW,
    text: "Deputy Review",
  },
  {
    value: OrderProgressEnum.APPROVED,
    text: "Approved",
  },
  {
    value: APPROVAL_STATUS.NOT_APPROVED,
    text: "Not Approved",
  },
  // Warning Letter Statuses that are not in ORDER
  {
    value: WarningLetterProgressEnum.ISSUED,
    text: "Issued",
  },
  // AP Referral Statuses that are not in OTHER ENFORCEMENT ACTIONS
  {
    value: APReferralStatus.CEB_NOT_PROCEEDING.id,
    text: "CEB Not Proceeding",
  },
  {
    value: APReferralStatus.REFERRED_TO_DM.id,
    text: "Referred to DM",
  },
  // Violation Ticket Statuses that are not in OTHER ENFORCEMENT ACTIONS
  {
    value: ViolationTicketStatus.PAID,
    text: "Paid",
  },
  {
    value: ViolationTicketStatus.DISPUTED,
    text: "Disputed",
  },
  // CR Statuses that are not in OTHER ENFORCEMENT ACTIONS
  {
    value: CRStatus.SUBMITTED_TO_CROWN_COUNSEL.id,
    text: "Submitted to Crown Counsel",
  },
];
