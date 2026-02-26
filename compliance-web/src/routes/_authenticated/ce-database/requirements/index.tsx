import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useAuth } from "react-oidc-context";
import { Box, CircularProgress, Typography, useMediaQuery } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import type {
  MRT_ColumnFiltersState,
  MRT_SortingState,
  MRT_TableInstance,
  MRT_TableState,
  MRT_Updater,
} from "material-react-table";
import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import Pagination from "@/components/Shared/Pagination";
import RequirementsExternalFilters from "@/components/App/RequirementsGrid/RequirementsExternalFilters";
import ShowOnlyMyRequirementsSwitch from "@/components/App/RequirementsGrid/ShowOnlyMyRequirementsSwitch";
import RequirementsGridExport from "@/components/App/RequirementsGrid/RequirementsGridExport";
import { useTopicsData } from "@/hooks/useTopics";
import { useRequirementSourcesData } from "@/hooks/useComplaints";
import {
  useComplianceFindingsData,
  useEnforcementActionsData,
} from "@/hooks/useInspectionRequirements";
import { useInspectionRequirementsGrid } from "@/hooks/useInspectionRequirementsGrid";
import { useStaffUsersData } from "@/hooks/useStaff";
import {
  useConvertFiltersToQueryParams,
  useRequirementsGridColumns,
} from "@/components/App/RequirementsGrid/RequirementsGridUtils";
import type {
  InspectionRequirementGrid,
  InspectionRequirementGridQueryParams,
} from "@/models/InspectionRequirementGrid";
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
  const { data: staffUsers, isLoading: staffLoading } = useStaffUsersData({ isActive: true, otherPositions: false });
  const { user: currentUser, isLoading: authLoading } = useAuth();
  const isMdToLg = useMediaQuery(MQ.mdToLg);
    
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

  // Ref to ensure filters are only initialized once
  const filtersInitialized = useRef(false);
  const [isRestored, setIsRestored] = useState(false);

  // Get cached filters store methods
  const { getFilters, getExternalFilters, getSorting, hasHydrated } = cachedFiltersStore();

  const cachedColumnFilters = getFilters(requirementsColumnFiltersCacheKey);
  const cachedExternalFilters = getExternalFilters(requirementsColumnFiltersCacheKey);
  const cachedSorting = getSorting(requirementsColumnFiltersCacheKey);

  const currentStaff = useMemo(() => {
    if (!currentUser?.profile?.preferred_username || !staffUsers) return null;
    return staffUsers.find(
      (staff) => staff.auth_user_guid === currentUser.profile.preferred_username
    );
  }, [currentUser, staffUsers]);

  // Initialize filters only once when all data is ready
  useEffect(() => {
    // Don't initialize if already done, or if required data isn't loaded yet
    if (!hasHydrated || filtersInitialized.current || authLoading || staffLoading || !currentStaff) {
      return;
    }

    filtersInitialized.current = true;

    // Check if we have cached filters
     const hasCachedFilters =
      (Array.isArray(cachedColumnFilters) &&
        cachedColumnFilters.length > 0) ||
      (cachedExternalFilters &&
        Object.keys(cachedExternalFilters).length > 0) ||
      (cachedSorting &&
        Array.isArray(cachedSorting) &&
        cachedSorting.length > 0);

    if (hasCachedFilters) {
      // Restore from cache
      if (cachedColumnFilters.length > 0) {
        setColumnFilters(cachedColumnFilters);
      }
      
      if (cachedExternalFilters) {
        const restoredExternalFilters = cachedExternalFilters as Record<
          string,
          string[] | string
        >;
        
        // Restore external filters
        setExternalFilters(restoredExternalFilters);

        // Restore switch state
        if (restoredExternalFilters.myRequirementsChecked !== undefined) {
          setMyRequirementsChecked(Boolean(restoredExternalFilters.myRequirementsChecked));
        } else {
          // Derive from primary_officer filter
          const primaryOfficer = restoredExternalFilters.primary_officer_ids;
          const derivedState =
            Array.isArray(primaryOfficer) &&
            primaryOfficer.some((id) => Boolean(id));
          setMyRequirementsChecked(derivedState);
        }

        // Restore global filter
        if (restoredExternalFilters.globalFilter) {
          setGlobalFilter(restoredExternalFilters.globalFilter as string);
        }
      }

      // Restore sorting
      if (cachedSorting && Array.isArray(cachedSorting) && cachedSorting.length > 0 && cachedSorting[0]?.id) {
        setSorting(cachedSorting);
      }
    } else {
      // No cached filters - apply default "My Requirements" filter
      const defaultExternalFilters = {
        primary_officer_ids: [currentStaff.id.toString()],
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
    }

    setIsRestored(true);
  }, [
    authLoading,
    staffLoading,
    currentStaff,
    cachedColumnFilters,
    cachedExternalFilters,
    cachedSorting,
    hasHydrated,
  ]);

  // Cache filters when they change
  const cacheTimeoutRef = useRef<NodeJS.Timeout>();
  useEffect(() => {
    // Only cache after filters are initialized
    if (!filtersInitialized.current || !isRestored) return;

    // Clear existing timeout
    if (cacheTimeoutRef.current) {
      clearTimeout(cacheTimeoutRef.current);
    }

    // Debounce the cache operation
    cacheTimeoutRef.current = setTimeout(() => {
      cachedFiltersStore.getState().setFilters(
        requirementsColumnFiltersCacheKey,
        columnFilters,
        {
          ...externalFilters,
          myRequirementsChecked,
          globalFilter,
        },
        sorting
      );
    }, 300);

    return () => {
      if (cacheTimeoutRef.current) {
        clearTimeout(cacheTimeoutRef.current);
      }
    };
  }, [columnFilters, externalFilters, myRequirementsChecked, globalFilter, sorting, isRestored]);

  const convertFiltersToQueryParams = useConvertFiltersToQueryParams(externalFilters);

  const queryParams: InspectionRequirementGridQueryParams = useMemo(() => {
    const currentSort = sorting[0];

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

// Column filter handler that enforces "My Requirements" toggle
  const handleColumnFiltersChange = useCallback(
    (updater: MRT_Updater<MRT_ColumnFiltersState>) => {
      setColumnFilters((prevFilters) => {
        const newFilters = typeof updater === 'function' ? updater(prevFilters) : updater;
        
        // If "My Requirements" is checked, ensure primary_officer filter is present
        if (myRequirementsChecked && currentStaff) {
          const hasPrimaryOfficerFilter = newFilters.some(
            (filter) => filter.id === "primary_officer"
          );
          
          // If user removed the primary_officer filter, re-add it
          if (!hasPrimaryOfficerFilter) {
            const primaryOfficerFilter = {
              id: "primary_officer",
              value: [currentStaff.id.toString()],
            };
            // Update external filters to keep them in sync
            setExternalFilters((prev) => ({
              ...prev,
              primary_officer_id: [currentStaff.id.toString()],
            }));
            return [...newFilters, primaryOfficerFilter];
          }
        }
        
        return newFilters;
      });
    },
    [myRequirementsChecked, currentStaff]
  );

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
    setSorting([{ id: "tpc", desc: false }]);
    setPagination((prev) => ({ ...prev, pageIndex: 0 }));

    cachedFiltersStore.getState().clearFilters(requirementsColumnFiltersCacheKey);
  }, []);

  // Handle "My Requirements" switch changes
  const handleMyRequirementsSwitchChange = useCallback(
    (filters: {
      checked: boolean;
      externalFilters: Record<string, string[] | string>;
      columnFilters?: MRT_TableState<InspectionRequirementGrid>["columnFilters"];
    }) => {
      setMyRequirementsChecked(filters.checked);
      setExternalFilters(filters.externalFilters);
      setPagination((prev) => ({ ...prev, pageIndex: 0 }));

      if (filters.columnFilters !== undefined) {
        if (filters.checked) {
          setColumnFilters((prevFilters) => {
            const filteredFilters = prevFilters.filter(
              (filter) => filter.id !== "primary_officer"
            );
            return [...filteredFilters, ...filters.columnFilters!];
          });
        } else {
          setColumnFilters((prevFilters) =>
            prevFilters.filter((filter) => filter.id !== "primary_officer")
          );
        }
      }
    },
    []
  );

  const columns = useRequirementsGridColumns({
    topics,
    complianceFindings,
    enforcementActions,
    requirementSources,
  });

  // Show loading state until everything is ready
  if (authLoading || staffLoading || !isRestored) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="100%"
      >
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <MasterDataTable
      columns={columns}
      data={requirementsList}
      initialState={{
        sorting: sorting,
        columnFilters: columnFilters,
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
              alignItems: isMdToLg ? "flex-start" : "center",
              flexDirection: isMdToLg ? "column" : "row",
              gap: isMdToLg ? 2 : 0,
              justifyContent: "space-between",
              width: "100%",
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
