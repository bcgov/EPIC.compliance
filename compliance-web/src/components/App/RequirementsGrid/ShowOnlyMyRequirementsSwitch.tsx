import { FormControlLabel, Typography, CircularProgress } from "@mui/material";
import CustomSwitch from "@/components/Shared/Controlled/CustomSwitch";
import { useAuth } from "react-oidc-context";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useMemo, useCallback, useState, useEffect } from "react";
import { STAFF_USER_POSITION, APPROVAL_STATUS } from "@/utils/constants";
import { MRT_TableState } from "material-react-table";
import { InspectionRequirementGrid } from "@/models/InspectionRequirementGrid";

interface ShowOnlyMyRequirementsSwitchProps {
  disabled?: boolean;
  onFiltersChange?: (filters: {
    checked: boolean;
    externalFilters: Record<string, string[] | string>;
    columnFilters?: MRT_TableState<InspectionRequirementGrid>["columnFilters"];
  }) => void;
  initialChecked?: boolean;
  onColumnFiltersChange?: (
    updater:
      | MRT_TableState<InspectionRequirementGrid>["columnFilters"]
      | ((
          old: MRT_TableState<InspectionRequirementGrid>["columnFilters"]
        ) => MRT_TableState<InspectionRequirementGrid>["columnFilters"])
  ) => void;
}

const ShowOnlyMyRequirementsSwitch: React.FC<
  ShowOnlyMyRequirementsSwitchProps
> = ({ 
  disabled = false,
  onFiltersChange,
  initialChecked = false,
  onColumnFiltersChange
}) => {
  const { user: currentUser, isLoading: authLoading } = useAuth();
  const { data: staffUsers, isLoading: staffLoading } = useStaffUsersData();
  
  // Internal state management
  const [checked, setChecked] = useState(initialChecked);

  // Update internal state when initialChecked changes (for restoration)
  useEffect(() => {
    setChecked(initialChecked);
  }, [initialChecked]);

  // Find current user in staff list
  const currentStaff = useMemo(() => {
    if (!currentUser?.profile?.preferred_username || !staffUsers)
      return undefined;
    return staffUsers.find(
      (staff) => staff.auth_user_guid === currentUser.profile.preferred_username
    );
  }, [currentUser?.profile?.preferred_username, staffUsers]);

  // Check if current user is a deputy director
  const isCurrentUserDeputy = useMemo(() => {
    return currentStaff?.position_id === STAFF_USER_POSITION.DEPUTY_DIRECTOR;
  }, [currentStaff?.position_id]);

  // Determine if switch should be disabled
  const isSwitchDisabled = useMemo(() => {
    return disabled || authLoading || staffLoading || !currentStaff;
  }, [disabled, authLoading, staffLoading, currentStaff]);

  // Get the appropriate label based on user role
  const getSwitchLabel = useMemo(() => {
    if (isCurrentUserDeputy) {
      return `${currentUser?.profile?.given_name}'s Files for Review`;
    } else {
      return `${currentUser?.profile?.given_name}'s Files`;
    }
  }, [isCurrentUserDeputy, currentUser?.profile?.given_name]);

  // Generate external filters based on current state
  const generateExternalFilters = useCallback((isChecked: boolean): Record<string, string[] | string> => {
    if (!isChecked || !currentStaff?.id) {
      return {
        primary_officer_id: [],
        approver_ids: [],
        approval_status: [],
      };
    }

    if (isCurrentUserDeputy) {
      // For deputy directors, filter by both reviewer and approval status
      return {
        approver_ids: [currentStaff.id.toString()],
        approval_status: [APPROVAL_STATUS.APPROVAL_PENDING],
      };
    } else {
      // For regular users, filter by primary officer
      return {
        primary_officer_id: [currentStaff.id.toString()],
      };
    }
  }, [currentStaff?.id, isCurrentUserDeputy]);

  // Generate column filters for UI display (deputy directors only)
  const generateColumnFilters = useCallback((isChecked: boolean): MRT_TableState<InspectionRequirementGrid>["columnFilters"] => {
    if (!isChecked || !isCurrentUserDeputy || !currentStaff) {
      return [];
    }

    const currentUserStaff = staffUsers?.find(staff => staff.id === currentStaff.id);
    return [
      {
        id: "approver",
        value: [currentUserStaff?.name || ""],
      },
      {
        id: "apprv_sts",
        value: [APPROVAL_STATUS.APPROVAL_PENDING],
      },
    ];
  }, [isCurrentUserDeputy, currentStaff, staffUsers]);

  // Handle switch change
  const handleSwitchChange = useCallback((newChecked: boolean) => {
    setChecked(newChecked);
    
    const externalFilters = generateExternalFilters(newChecked);
    const columnFilters = generateColumnFilters(newChecked);
    
    // Notify parent of filter changes
    onFiltersChange?.({
      checked: newChecked,
      externalFilters,
      columnFilters,
    });
    
    // Update column filters for UI display if callback provided
    if (onColumnFiltersChange) {
      if (newChecked && isCurrentUserDeputy) {
        // Remove existing user-specific filters and add new ones
        const filteredFilters = columnFilters.filter(
          (filter) =>
            filter.id !== "approver" && filter.id !== "apprv_sts"
        );
        onColumnFiltersChange([...filteredFilters, ...generateColumnFilters(true)]);
      } else {
        // Remove user-specific filters when turning off
        const filteredFilters = columnFilters.filter(
          (filter) =>
            filter.id !== "approver" && filter.id !== "apprv_sts"
        );
        onColumnFiltersChange(filteredFilters);
      }
    }
  }, [generateExternalFilters, generateColumnFilters, onFiltersChange, onColumnFiltersChange, isCurrentUserDeputy]);

  if (authLoading || staffLoading) {
    return <CircularProgress size={24} />;
  }

  return (
    <FormControlLabel
      control={
        <CustomSwitch
          checked={checked}
          onChange={(_, value) => handleSwitchChange(value)}
          size="small"
          disabled={isSwitchDisabled}
        />
      }
      label={
        <Typography variant="body1" mr={1}>
          <strong>{getSwitchLabel}</strong>
        </Typography>
      }
      labelPlacement="start"
      sx={{
        marginRight: -1,
      }}
    />
  );
};

export default ShowOnlyMyRequirementsSwitch;
