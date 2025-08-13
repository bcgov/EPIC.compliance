import { FormControlLabel, Typography, CircularProgress } from "@mui/material";
import CustomSwitch from "@/components/Shared/Controlled/CustomSwitch";
import { useAuth } from "react-oidc-context";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useMemo, useCallback, useState, useEffect } from "react";
import { MRT_TableState } from "material-react-table";
import { CaseFile } from "@/models/CaseFile";

interface ShowOnlyMyCaseFilesSwitchProps {
  disabled?: boolean;
  onFiltersChange?: (filters: {
    checked: boolean;
    externalFilters: Record<string, string[] | string>;
    columnFilters?: MRT_TableState<CaseFile>["columnFilters"];
  }) => void;
  initialChecked?: boolean;
  onColumnFiltersChange?: (
    updater:
      | MRT_TableState<CaseFile>["columnFilters"]
      | ((
          old: MRT_TableState<CaseFile>["columnFilters"]
        ) => MRT_TableState<CaseFile>["columnFilters"])
  ) => void;
}

const ShowOnlyMyCaseFilesSwitch: React.FC<
  ShowOnlyMyCaseFilesSwitchProps
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
          status: [],
        };
      }

      // For regular users, filter by primary officer and status 'open'
      return {
        primary_officer_id: [currentStaff.id.toString()],
        status: ["Open"],
      };
    },
    [currentStaff?.id]
  );

  // Generate column filters for UI display
  const generateColumnFilters = useCallback(
    (isChecked: boolean): MRT_TableState<CaseFile>["columnFilters"] => {
      if (!isChecked || !currentStaff) {
        return [];
      }

      const currentUserStaff = staffUsers?.find(
        (staff) => staff.id === currentStaff.id
      );
      return [
        {
          id: "primary_officer",
          value: [currentUserStaff?.name || ""],
        },
        {
          id: "status",
          value: ["Open"],
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
            (filter) => filter.id !== "primary_officer"
          );
          onColumnFiltersChange([
            ...filteredFilters,
            ...generateColumnFilters(true),
          ]);
        } else {
          // Remove user-specific filters when turning off
          const filteredFilters = columnFilters.filter(
            (filter) => filter.id !== "primary_officer"
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

export default ShowOnlyMyCaseFilesSwitch;
