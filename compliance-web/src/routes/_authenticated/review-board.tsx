import ReviewBoardFilters from "@/components/App/ReviewBoard/ReviewBoardFilters";
import ReviewBoardSection from "@/components/App/ReviewBoard/ReviewBoardSection";
import {
  useFetchAdminstrativePenalties,
  useFetchInspectionRecords,
  useFetchOrderRecords,
  useFetchWarningLetters,
} from "@/hooks/useReviewBoard";
import { generateDynamicSections } from "@/components/App/ReviewBoard/ReviewBoardUtils";
import { useStaffUsersData } from "@/hooks/useStaff";
import { cachedFiltersStore } from "@/store/cachedFiltersStore";
import { Box, Typography, CircularProgress } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { useAuth } from "react-oidc-context";

export const Route = createFileRoute("/_authenticated/review-board")({
  component: ReviewBoard,
});

const reviewBoardColumnFiltersCacheKey = "review-board-column-filters";

function ReviewBoard() {
  const { data: inspectionRecords } = useFetchInspectionRecords();
  const { data: orderRecords } = useFetchOrderRecords();
  const { data: warningLetters } = useFetchWarningLetters();
  const { data: administrativePenalties } = useFetchAdminstrativePenalties();
  const { data: staffUsers, isLoading: staffLoading } = useStaffUsersData();
  const { user: currentUser, isLoading: authLoading } = useAuth();

  const [externalFilters, setExternalFilters] = useState<
    Record<string, string[] | string>
  >({});
  const [initialChecked, setInitialChecked] = useState(false);

  // Create the exact 6 sections like mockReviewBoard and populate with dynamic data
  const dynamicSections = useMemo(() => {
    // Extract primary officer filter from external filters
    const primaryOfficerFilter = externalFilters.primary_officer_id as string[] | undefined;
    
    return generateDynamicSections(
      inspectionRecords,
      orderRecords,
      warningLetters,
      administrativePenalties,
      primaryOfficerFilter
    );
  }, [
    inspectionRecords,
    orderRecords,
    warningLetters,
    administrativePenalties,
    externalFilters.primary_officer_id,
  ]);

  // Track if we're in the initial load phase to prevent caching during restoration
  const isInitialLoad = useRef(true);
  const [isRestored, setIsRestored] = useState(false);

  // Track previous values to prevent unnecessary caching
  const prevFilters = useRef<{
    externalFilters: Record<string, string[] | string>;
    initialChecked: boolean;
  }>({
    externalFilters: {},
    initialChecked: false,
  });

  // Get cached filters store methods
  const { getExternalFilters } = cachedFiltersStore();
  const cachedExternalFilters = getExternalFilters(
    reviewBoardColumnFiltersCacheKey
  );

  // Restore cached filters on component mount
  useEffect(() => {
    // Reset the initial load flag on every mount
    isInitialLoad.current = true;

    if (cachedExternalFilters) {
      const restoredExternalFilters = cachedExternalFilters as Record<
        string,
        string[] | string
      >;
      setExternalFilters(restoredExternalFilters);

      // Restore "My Files" switch state if it was cached
      if (restoredExternalFilters.myFilesChecked !== undefined) {
        const restoredSwitchState = Boolean(
          restoredExternalFilters.myFilesChecked
        );
        setInitialChecked(restoredSwitchState);
      } else {
        // Fallback: derive from primary_officer filter if switch state not stored
        const primaryOfficerFilter =
          restoredExternalFilters.primary_officer_id || [];
        const derivedSwitchState = !!(primaryOfficerFilter?.length > 0);
        setInitialChecked(derivedSwitchState);
      }
    } else {
      // No cached filters - apply default "My Files" filter for first-time users
      if (currentUser?.profile?.preferred_username && staffUsers) {
        const currentStaff = staffUsers.find(
          (staff) =>
            staff.auth_user_guid === currentUser.profile.preferred_username
        );
        if (currentStaff) {
          const defaultExternalFilters = {
            primary_officer_id: [currentStaff.id.toString()],
          };

          setExternalFilters(defaultExternalFilters);
          setInitialChecked(true);

          // Update prevFilters to prevent unnecessary caching during initial setup
          prevFilters.current = {
            ...prevFilters.current,
            externalFilters: defaultExternalFilters,
            initialChecked: true,
          };
        }
      }
    }

    // Mark restoration as complete and initial load as complete
    isInitialLoad.current = false;
    setIsRestored(true);
  }, [cachedExternalFilters, staffUsers, currentUser]);

  // Cache all filters when they change (but not during initial load)
  useEffect(() => {
    if (!isInitialLoad.current) {
      // Check if any values have actually changed
      const currentFilters = {
        externalFilters,
        initialChecked,
      };

      const hasChanged =
        JSON.stringify(currentFilters) !== JSON.stringify(prevFilters.current);

      if (hasChanged) {
        cachedFiltersStore.getState().setFilters(
          reviewBoardColumnFiltersCacheKey,
          [], // No column filters for review board
          {
            ...externalFilters,
            myFilesChecked: initialChecked, // Store the switch state explicitly
          },
          [] // No sorting for review board
        );

        // Update previous values
        prevFilters.current = currentFilters;
      }
    }
  }, [externalFilters, initialChecked]);

  const handleFilterChange = useCallback(
    (filterId: string, value: string[] | string) => {
      setExternalFilters((prev) => ({
        ...prev,
        [filterId]: value,
      }));
    },
    []
  );

  const handleSwitchChange = useCallback((checked: boolean) => {
    setInitialChecked(checked);
  }, []);

  return authLoading || staffLoading || !isRestored ? (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="100%"
    >
      <CircularProgress size={60} />
    </Box>
  ) : (
    <Box
      sx={{ display: "flex", flexDirection: "column", gap: 2, height: "100%" }}
    >
      <Box
        sx={{
          width: "100%",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Typography
          variant="h5"
          sx={{ color: BCDesignTokens.typographyColorLink }}
        >
          Review Board
        </Typography>
        <ReviewBoardFilters
          onFilterChange={handleFilterChange}
          externalFilters={externalFilters}
          initialChecked={initialChecked}
          onSwitchChange={handleSwitchChange}
        />
      </Box>
      <Box sx={{ display: "flex", gap: 1, overflow: "auto", flex: 1 }}>
        {dynamicSections.map((section) => (
          <ReviewBoardSection key={section.id} section={section} />
        ))}
      </Box>
    </Box>
  );
}
