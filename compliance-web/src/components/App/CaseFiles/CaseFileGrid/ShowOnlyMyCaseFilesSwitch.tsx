import { FormControlLabel, Typography, CircularProgress } from "@mui/material";
import CustomSwitch from "@/components/Shared/Controlled/CustomSwitch";
import { useAuth } from "react-oidc-context";
import { useMemo, useCallback, useState, useEffect } from "react";
import { MRT_TableState } from "material-react-table";
import { CaseFile } from "@/models/CaseFile";
import { StaffUser } from "@/models/Staff";

interface ShowOnlyMyCaseFilesSwitchProps {
  disabled?: boolean;
  staffUsers: StaffUser[];
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

const ShowOnlyMyCaseFilesSwitch: React.FC<ShowOnlyMyCaseFilesSwitchProps> = ({
  disabled = false,
  staffUsers,
  onFiltersChange,
  initialChecked = true, // Default to true as per requirement #5
  onColumnFiltersChange,
}) => {
  const { user: currentUser, isLoading: authLoading } = useAuth();

  // Internal state management
  const [checked, setChecked] = useState(initialChecked);

  // Find current user in staff list
  const currentStaff = useMemo(() => {
    if (!currentUser?.profile?.preferred_username || !staffUsers) return undefined;
    return staffUsers.find(
      (staff) => staff.auth_user_guid === currentUser.profile.preferred_username
    );
  }, [currentUser?.profile?.preferred_username, staffUsers]);

  // Determine if switch should be disabled
  const isSwitchDisabled = useMemo(() => {
    return disabled || authLoading || !currentStaff;
  }, [disabled, authLoading, currentStaff]);

  // Get the appropriate label
  const switchLabel = useMemo(() => {
    return `${currentUser?.profile?.given_name || 'My'} Files`;
  }, [currentUser?.profile?.given_name]);

  // Generate external filters for API calls
  const generateExternalFilters = useCallback(
    (isChecked: boolean): Record<string, string[] | string> => {
      if (!isChecked || !currentStaff?.id) {
        return {};
      }
      return {
        primary_officer_ids: [currentStaff.id.toString()],
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
      return [
        {
          id: "primary_officer",
          value: [currentStaff.id.toString()],
        },
      ];
    },
    [currentStaff]
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
          // When turning ON, replace any existing primary_officer filter with current user
          onColumnFiltersChange((prevFilters) => {
            const filteredFilters = prevFilters.filter(
              (filter) => filter.id !== "primary_officer"
            );
            return [...filteredFilters, ...columnFilters];
          });
        } else {
          // When turning OFF, remove the primary_officer filter but keep others
          onColumnFiltersChange((prevFilters) => {
            return prevFilters.filter(
              (filter) => filter.id !== "primary_officer"
            );
          });
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

  // Update internal state when initialChecked changes (for restoration)
  useEffect(() => {
    setChecked(initialChecked);
  }, [initialChecked]);

  if (authLoading) {
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
          <strong>{switchLabel}</strong>
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
