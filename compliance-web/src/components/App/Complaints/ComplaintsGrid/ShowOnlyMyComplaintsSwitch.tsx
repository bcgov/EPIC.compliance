import { FormControlLabel, Typography, CircularProgress } from "@mui/material";
import CustomSwitch from "@/components/Shared/Controlled/CustomSwitch";
import { useAuth } from "react-oidc-context";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useMemo, useCallback, useState, useEffect } from "react";
import { MRT_TableState } from "material-react-table";
import { Complaint } from "@/models/Complaint";

interface ShowOnlyMyComplaintsSwitchProps {
  disabled?: boolean;
  onFiltersChange?: (filters: {
    checked: boolean;
    externalFilters: Record<string, string[] | string>;
    columnFilters?: MRT_TableState<Complaint>["columnFilters"];
  }) => void;
  initialChecked?: boolean;
  onColumnFiltersChange?: (
    updater:
      | MRT_TableState<Complaint>["columnFilters"]
      | ((
          old: MRT_TableState<Complaint>["columnFilters"]
        ) => MRT_TableState<Complaint>["columnFilters"])
  ) => void;
}

const ShowOnlyMyComplaintsSwitch: React.FC<
  ShowOnlyMyComplaintsSwitchProps
> = ({
  disabled = false,
  onFiltersChange,
  initialChecked = false,
  onColumnFiltersChange,
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

  // Determine if switch should be disabled
  const isSwitchDisabled = useMemo(() => {
    return disabled || authLoading || staffLoading || !currentStaff;
  }, [disabled, authLoading, staffLoading, currentStaff]);

  // Get the appropriate label
  const getSwitchLabel = useMemo(() => {
    return `${currentUser?.profile?.given_name}'s Files`;
  }, [currentUser?.profile?.given_name]);

  // Generate external filters based on current state
  const generateExternalFilters = useCallback(
    (isChecked: boolean): Record<string, string[] | string> => {
      if (!isChecked || !currentStaff?.id) {
        return {
          primary_officer_id: [],
        };
      }

      // For regular users, filter by primary officer
      return {
        primary_officer_id: [currentStaff.id.toString()],
      };
    },
    [currentStaff?.id]
  );

  // Generate column filters for UI display
  const generateColumnFilters = useCallback(
    (isChecked: boolean): MRT_TableState<Complaint>["columnFilters"] => {
      if (!isChecked || !currentStaff) {
        return [];
      }

      const currentUserStaff = staffUsers?.find(
        (staff) => staff.id === currentStaff.id
      );
      return [
        {
          id: "primary_officer_id",
          value: [currentUserStaff?.name || ""],
        },
      ];
    },
    [currentStaff, staffUsers]
  );

  // Handle switch change
  const handleSwitchChange = useCallback(
    (newChecked: boolean) => {
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
        if (newChecked) {
          // Remove existing user-specific filters and add new ones
          const filteredFilters = columnFilters.filter(
            (filter) => filter.id !== "primary_officer_id"
          );
          onColumnFiltersChange([
            ...filteredFilters,
            ...generateColumnFilters(true),
          ]);
        } else {
          // Remove user-specific filters when turning off
          const filteredFilters = columnFilters.filter(
            (filter) => filter.id !== "primary_officer_id"
          );
          onColumnFiltersChange(filteredFilters);
        }
      }
    },
    [
      generateExternalFilters,
      generateColumnFilters,
      onFiltersChange,
      onColumnFiltersChange,
    ]
  );

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

export default ShowOnlyMyComplaintsSwitch;
