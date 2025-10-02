import {
  Box,
  CircularProgress,
  FormControlLabel,
  Typography,
} from "@mui/material";
import ExternalTableFilter from "@/components/Shared/FilterSelect/ExternalTableFilter";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useCallback, useEffect, useMemo, useState } from "react";
import CustomSwitch from "@/components/Shared/Controlled/CustomSwitch";
import { useAuth } from "react-oidc-context";

interface ReviewBoardFiltersProps {
  onFilterChange: (filterId: string, value: string[] | string) => void;
  externalFilters: Record<string, string[] | string>;
  initialChecked: boolean;
  onSwitchChange?: (checked: boolean) => void;
}

const ReviewBoardFilters: React.FC<ReviewBoardFiltersProps> = ({
  onFilterChange,
  externalFilters,
  initialChecked,
  onSwitchChange,
}) => {
  const { user: currentUser, isLoading: authLoading } = useAuth();
  const { data: staffUsers, isLoading: staffLoading } = useStaffUsersData();

  // Internal state management
  const [checked, setChecked] = useState(initialChecked);

  // Update internal state when initialChecked changes (for restoration)
  useEffect(() => {
    setChecked(initialChecked);
  }, [initialChecked]);

  const primaryOfficerOptions = useMemo(
    () =>
      staffUsers?.map((user) => ({
        text: user.name,
        value: user.id.toString(),
      })) ?? [],
    [staffUsers]
  );

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
    return authLoading || staffLoading || !currentStaff;
  }, [authLoading, staffLoading, currentStaff]);

  // Handle switch change
  const handleSwitchChange = useCallback(
    (newChecked: boolean) => {
      setChecked(newChecked);

      if (newChecked && currentStaff) {
        // When turning ON, set the primary officer filter to current user
        onFilterChange("primary_officer_id", [currentStaff.id.toString()]);
      } else {
        // When turning OFF, clear the primary officer filter
        onFilterChange("primary_officer_id", []);
      }

      // Notify parent so it can persist switch state explicitly
      onSwitchChange?.(newChecked);
    },
    [currentStaff, onFilterChange, onSwitchChange]
  );

  if (authLoading || staffLoading) {
    return <CircularProgress size={24} />;
  }

  return (
    <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
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
            <strong>{`${currentUser?.profile?.given_name}'s Files`}</strong>
          </Typography>
        }
        labelPlacement="start"
        sx={{
          marginRight: -1,
        }}
      />
    </Box>
  );
};

export default ReviewBoardFilters;
