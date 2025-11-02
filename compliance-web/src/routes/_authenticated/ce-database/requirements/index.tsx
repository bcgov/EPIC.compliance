import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import { useRequirementSourcesData } from "@/hooks/useComplaints";
import {
  useComplianceFindingsData,
  useEnforcementActionsData,
} from "@/hooks/useInspectionRequirements";
import { useInspectionRequirementsGrid } from "@/hooks/useInspectionRequirementsGrid";
import { useTopicsData } from "@/hooks/useTopics";
import {
  InspectionRequirementGrid,
  InspectionRequirementGridQueryParams,
} from "@/models/InspectionRequirementGrid";
import { Box, CircularProgress, Typography } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import {
  MRT_TableState,
  MRT_SortingState,
  MRT_TableInstance,
} from "material-react-table";
import { useMemo, useState, useCallback, useEffect, useRef } from "react";
import { useAuth } from "react-oidc-context";
import RequirementsExternalFilters from "@/components/App/RequirementsGrid/RequirementsExternalFilters";
import ShowOnlyMyRequirementsSwitch from "@/components/App/RequirementsGrid/ShowOnlyMyRequirementsSwitch";
import Pagination from "@/components/Shared/Pagination";
import RequirementsGridExport from "@/components/App/RequirementsGrid/RequirementsGridExport";
import {
  useConvertFiltersToQueryParams,
  useRequirementsGridColumns,
} from "@/components/App/RequirementsGrid/RequirementsGridUtils";
import { useStaffUsersData } from "@/hooks/useStaff";
import { cachedFiltersStore } from "@/store/cachedFiltersStore";
import { useTableHandlers } from "@/components/Shared/MasterDataTable/useTableHandlers";
import { AppConfig } from "@/utils/config";
import { MQ } from "@/styles/responsive";

export const Route = createFileRoute(
  "/_authenticated/ce-database/requirements/"
)({
  component: Requirements,
});

const requirementsColumnFiltersCacheKey = "requirements-column-filters";

function Requirements() {
  const { data: topics } = useTopicsData();
  const { data: complianceFindings } = useComplianceFindingsData();
  const { data: enforcementActions } = useEnforcementActionsData();
  const { data: requirementSources } = useRequirementSourcesData();
  const { data: staffUsers, isLoading: staffLoading } = useStaffUsersData();
  const { user: currentUser, isLoading: authLoading } = useAuth();

  // State for "My Requirements" switch - default to true for first-time users
  const [myRequirementsChecked, setMyRequirementsChecked] = useState(true);
  const [sorting, setSorting] = useState<MRT_SortingState>([
    { id: "tpc", desc: false },
  ]);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: AppConfig.defaultPageSize,
  });

  const [columnFilters, setColumnFilters] = useState<
    MRT_TableState<InspectionRequirementGrid>["columnFilters"]
  >([]);
  const [globalFilter, setGlobalFilter] = useState<string>("");
  const [externalFilters, setExternalFilters] = useState<
    Record<string, string[] | string>
  >({});

  // Track if we're in the initial load phase to prevent caching during restoration
  const isInitialLoad = useRef(true);
  const [isRestored, setIsRestored] = useState(false);

  // Track previous values to prevent unnecessary caching
  const prevFilters = useRef<{
    columnFilters: MRT_TableState<InspectionRequirementGrid>["columnFilters"];
    externalFilters: Record<string, string[] | string>;
    myRequirementsChecked: boolean;
    globalFilter: string;
    sorting: MRT_SortingState;
  }>({
    columnFilters: [],
    externalFilters: {},
    myRequirementsChecked: true, // Default to true for first-time users
    globalFilter: "",
    sorting: [{ id: "tpc", desc: false }],
  });

  // Get cached filters store methods
  const { getFilters, getExternalFilters, getSorting } = cachedFiltersStore();
  const cachedColumnFilters = getFilters(requirementsColumnFiltersCacheKey);
  const cachedExternalFilters = getExternalFilters(
    requirementsColumnFiltersCacheKey
  );
  const cachedSorting = getSorting(requirementsColumnFiltersCacheKey);

  // Restore cached filters on component mount
  useEffect(() => {
    // Reset the initial load flag on every mount
    isInitialLoad.current = true;

    if (cachedColumnFilters.length > 0) {
      setColumnFilters(cachedColumnFilters);
    }
    if (cachedExternalFilters) {
      const restoredExternalFilters = cachedExternalFilters as Record<
        string,
        string[] | string
      >;
      setExternalFilters(restoredExternalFilters);

      // Restore "My Requirements" switch state if it was cached
      if (restoredExternalFilters.myRequirementsChecked !== undefined) {
        // Use the explicitly stored switch state
        const restoredSwitchState = Boolean(
          restoredExternalFilters.myRequirementsChecked
        );
        setMyRequirementsChecked(restoredSwitchState);

        // If switch is ON, ensure column filters are set up for UI display
        if (
          restoredSwitchState &&
          currentUser?.profile?.preferred_username &&
          staffUsers
        ) {
          const currentStaff = staffUsers.find(
            (staff) =>
              staff.auth_user_guid === currentUser.profile.preferred_username
          );
          if (currentStaff) {
            // Add primary_officer column filter for UI display
            const primaryOfficerColumnFilter = {
              id: "primary_officer",
              value: [currentStaff.id.toString()],
            };
            setColumnFilters((prev) => {
              const filtered = prev.filter(
                (filter) => filter.id !== "primary_officer"
              );
              return [...filtered, primaryOfficerColumnFilter];
            });
          }
        }
      } else {
        // Fallback: derive from primary_officer filter if switch state not stored
        const primaryOfficerFilter =
          restoredExternalFilters.primary_officer_id || [];
        const derivedSwitchState = !!(primaryOfficerFilter?.length > 0);
        setMyRequirementsChecked(derivedSwitchState);

        // If derived state is ON, ensure column filters are set up
        if (
          derivedSwitchState &&
          currentUser?.profile?.preferred_username &&
          staffUsers
        ) {
          const currentStaff = staffUsers.find(
            (staff) =>
              staff.auth_user_guid === currentUser.profile.preferred_username
          );
          if (currentStaff) {
            // Add primary_officer column filter for UI display
            const primaryOfficerColumnFilter = {
              id: "primary_officer",
              value: [currentStaff.id.toString()],
            };
            setColumnFilters((prev) => {
              const filtered = prev.filter(
                (filter) => filter.id !== "primary_officer"
              );
              return [...filtered, primaryOfficerColumnFilter];
            });
          }
        }
      }

      // Restore global filter if it was cached
      if (restoredExternalFilters.globalFilter) {
        setGlobalFilter(restoredExternalFilters.globalFilter as string);
      }
    } else {
      // No cached filters - apply default "My Requirements" filter for first-time users
      if (currentUser?.profile?.preferred_username && staffUsers) {
        const currentStaff = staffUsers.find(
          (staff) =>
            staff.auth_user_guid === currentUser.profile.preferred_username
        );
        if (currentStaff) {
          const defaultExternalFilters = {
            primary_officer_id: [currentStaff.id.toString()],
          };
          const defaultColumnFilters = [
            {
              id: "primary_officer",
              value: [currentStaff.id.toString()],
            },
          ];

          setExternalFilters(defaultExternalFilters);
          setColumnFilters(defaultColumnFilters);
          setMyRequirementsChecked(true);

          // Update prevFilters to prevent unnecessary caching during initial setup
          prevFilters.current = {
            ...prevFilters.current,
            externalFilters: defaultExternalFilters,
            columnFilters: defaultColumnFilters,
            myRequirementsChecked: true,
          };
        }
      }
    }

    // Restore sorting if it was cached
    if (cachedSorting && Array.isArray(cachedSorting)) {
      // Validate that it has the expected structure
      if (cachedSorting.length > 0 && cachedSorting[0]?.id) {
        setSorting(cachedSorting);
      }
    }

    // Mark restoration as complete and initial load as complete
    isInitialLoad.current = false;
    setIsRestored(true);
  }, [
    cachedColumnFilters,
    cachedExternalFilters,
    cachedSorting,
    staffUsers,
    currentUser,
  ]);

  // Cache all filters when they change (but not during initial load)
  useEffect(() => {
    if (!isInitialLoad.current) {
      // Check if any values have actually changed
      const currentFilters = {
        columnFilters,
        externalFilters,
        myRequirementsChecked,
        globalFilter,
        sorting,
      };

      const hasChanged =
        JSON.stringify(currentFilters) !== JSON.stringify(prevFilters.current);

      if (hasChanged) {
        cachedFiltersStore.getState().setFilters(
          requirementsColumnFiltersCacheKey,
          columnFilters,
          {
            ...externalFilters,
            myRequirementsChecked, // Store the switch state explicitly
            globalFilter,
          },
          sorting
        );

        // Update previous values
        prevFilters.current = currentFilters;
      }
    }
  }, [
    columnFilters,
    externalFilters,
    myRequirementsChecked,
    globalFilter,
    sorting,
  ]);

  // Use the extracted utility function
  const convertFiltersToQueryParams =
    useConvertFiltersToQueryParams(externalFilters);

  const queryParams: InspectionRequirementGridQueryParams = useMemo(() => {
    // Extract sorting information from the sorting state
    const currentSort = sorting[0]; // Material React Table supports multiple sorts, but we'll use the first one

    return {
      page_no: pagination.pageIndex + 1,
      page_size: pagination.pageSize,
      ...convertFiltersToQueryParams(columnFilters),
      ...(currentSort && {
        sort_by: currentSort.id,
        sort_order: currentSort.desc ? "desc" : "asc",
      }),
    };
  }, [
    pagination.pageIndex,
    pagination.pageSize,
    columnFilters,
    convertFiltersToQueryParams,
    sorting,
  ]);

  const { data, isLoading } = useInspectionRequirementsGrid(queryParams);
  const requirementsList = useMemo(() => data?.items ?? [], [data]);

  // Use the custom hook for table handlers
  const {
    handlePaginationChange,
    handleSortingChange,
    handleColumnFiltersChange,
    handleGlobalFilterChange,
  } = useTableHandlers({
    sorting,
    columnFilters,
    globalFilter,
    setSorting,
    setColumnFilters,
    setGlobalFilter,
    setPagination,
  });

  const handleExternalFilterChange = useCallback(
    (filterId: string, value: string[] | string) => {
      setExternalFilters((prev) => ({
        ...prev,
        [filterId]: value,
      }));
      setPagination((prev) => ({ ...prev, pageIndex: 0 }));
    },
    []
  );

  const handleClearAllFilters = useCallback(() => {
    setExternalFilters({});
    setColumnFilters([]);
    setGlobalFilter("");
    setMyRequirementsChecked(false);
    setSorting([{ id: "tpc", desc: false }]); // Reset to default sorting
    setPagination((prev) => ({ ...prev, pageIndex: 0 }));

    // Clear cached filters
    cachedFiltersStore
      .getState()
      .clearFilters(requirementsColumnFiltersCacheKey);
  }, []);

  // Handle "My Requirements" switch changes
  const handleMyRequirementsSwitchChange = useCallback(
    (filters: {
      checked: boolean;
      externalFilters: Record<string, string[] | string>;
      columnFilters?: MRT_TableState<InspectionRequirementGrid>["columnFilters"];
    }) => {
      // Only update if the values have actually changed
      const filtersChanged =
        JSON.stringify(filters.externalFilters) !==
        JSON.stringify(externalFilters);
      const checkedChanged = filters.checked !== myRequirementsChecked;

      if (checkedChanged) {
        setMyRequirementsChecked(filters.checked);
      }

      if (filtersChanged) {
        setExternalFilters(filters.externalFilters);
        // Reset pagination when filters change
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
      }

      // Update column filters if provided
      if (filters.columnFilters !== undefined) {
        if (filters.checked) {
          // When turning ON, merge with existing filters, replacing primary_officer if it exists
          handleColumnFiltersChange((prevFilters) => {
            const filteredFilters = prevFilters.filter(
              (filter) => filter.id !== "primary_officer"
            );
            return [...filteredFilters, ...filters.columnFilters!];
          });
        } else {
          // When turning OFF, remove primary_officer filter but keep others
          handleColumnFiltersChange((prevFilters) => {
            return prevFilters.filter(
              (filter) => filter.id !== "primary_officer"
            );
          });
        }
      }
    },
    [externalFilters, handleColumnFiltersChange, myRequirementsChecked]
  );

  // Use the extracted utility function for columns
  const columns = useRequirementsGridColumns({
    topics,
    complianceFindings,
    enforcementActions,
    requirementSources,
  });

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
    <MasterDataTable
      columns={columns}
      data={requirementsList ?? []}
      initialState={{
        sorting: sorting,
        columnFilters: isRestored ? columnFilters : [],
      }}
      state={{
        isLoading,
        showGlobalFilter: true,
        pagination,
        columnFilters,
        globalFilter,
        sorting,
      }}
      titleToolbarProps={{
        tableTitle: "Requirements",
      }}
      enableSorting={true}
      enablePagination={false}
      hideFilterToggle={true}
      renderTopToolbarCustomActions={({
        table,
      }: {
        table: MRT_TableInstance<InspectionRequirementGrid>;
      }) => (
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            gap: 2,
            width: "100%",
            mr: -1,
          }}
        >
          {/* Title section with toggle */}
          <Box
            sx={{
              width: "100%",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-end",
            }}
          >
            <Typography
              variant="h5"
              sx={{ color: BCDesignTokens.typographyColorLink }}
            >
              Requirements
            </Typography>
            <ShowOnlyMyRequirementsSwitch
              staffUsers={staffUsers ?? []}
              onFiltersChange={handleMyRequirementsSwitchChange}
              initialChecked={myRequirementsChecked}
            />
          </Box>

          {/* Pagination and controls section */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              width: "100%",
              [MQ.mdToLg]: {
                flexDirection: "column",
                alignItems: "flex-start",
                gap: 2
              },
            }}
          >
            {/* Left side - Export button */}
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <RequirementsGridExport queryParams={queryParams} />
              <Pagination
                currentPage={pagination.pageIndex}
                pageSize={pagination.pageSize}
                totalCount={data?.total || 0}
                onPreviousPage={() => table.previousPage()}
                onNextPage={() => table.nextPage()}
                canPreviousPage={table.getCanPreviousPage()}
                canNextPage={table.getCanNextPage()}
              />
            </Box>

            {/* Right side - Filters */}
            <RequirementsExternalFilters
              onFilterChange={handleExternalFilterChange}
              onClearAll={handleClearAllFilters}
              externalFilters={externalFilters}
            />
          </Box>
        </Box>
      )}
      remoteDataConfig={{
        enableRemoteData: true,
        rowCount: data?.total,
        onPaginationChange: handlePaginationChange,
        onColumnFiltersChange: handleColumnFiltersChange,
        onGlobalFilterChange: handleGlobalFilterChange,
        onSortingChange: handleSortingChange,
      }}
    />
  );
}
