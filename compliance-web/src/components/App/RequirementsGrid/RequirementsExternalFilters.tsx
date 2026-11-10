import { Box } from "@mui/material";
import ExternalTableFilter from "@/components/Shared/FilterSelect/ExternalTableFilter";
import ClearAllFiltersButton from "@/components/Shared/MasterDataTable/ClearAllFiltersButton";
import { InspectionStatusEnum } from "@/utils/constants";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useProjectsData } from "@/hooks/useProjects";
import { useMemo } from "react";

interface RequirementsExternalFiltersProps {
  onFilterChange: (filterId: string, value: string[] | string) => void;
  onClearAll: () => void;
  showClearAll: boolean;
  externalFilters: Record<string, string[] | string>;
}

const RequirementsExternalFilters: React.FC<
  RequirementsExternalFiltersProps
> = ({ onFilterChange, onClearAll, showClearAll, externalFilters }) => {
  const { data: staffUsers } = useStaffUsersData();
  const { data: projects } = useProjectsData();

  const inspectionStatusOptions = Object.entries(InspectionStatusEnum).map(
    ([key, value]) => ({
      text: value,
      value: key,
    })
  );

  const primaryOfficerOptions = useMemo(
    () =>
      staffUsers?.map((user) => ({
        text: user.name,
        value: user.id.toString(),
      })) ?? [],
    [staffUsers]
  );

  const projectOptions = useMemo(
    () =>
      projects?.map((project) => ({
        text: project.name,
        value: project.id.toString(),
      })) ?? [],
    [projects]
  );

  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
      <ExternalTableFilter
        filterId="project_id"
        filterOptions={projectOptions}
        onFilterChange={onFilterChange}
        placeholder="Project"
        variant="inline-standalone"
        isMulti={true}
        name="projectFilter"
        currentValue={externalFilters.project_id}
      />
      <ExternalTableFilter
        filterId="primary_officer_id"
        filterOptions={primaryOfficerOptions}
        onFilterChange={onFilterChange}
        placeholder="Primary"
        variant="inline-standalone"
        isMulti={true}
        name="primaryOfficerFilter"
        currentValue={externalFilters.primary_officer_id}
      />
      <ExternalTableFilter
        filterId="inspection_status"
        filterOptions={inspectionStatusOptions}
        onFilterChange={onFilterChange}
        placeholder="Inspection Status"
        variant="inline-standalone"
        isMulti={true}
        name="inspectionStatusFilter"
        currentValue={externalFilters.inspection_status}
      />
      {showClearAll && (
        <ClearAllFiltersButton onClick={onClearAll} />
      )}
    </Box>
  );
};

export default RequirementsExternalFilters;
