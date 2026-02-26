import { useEffect, useMemo, useState, useRef, useCallback } from "react";
import {
  MRT_TableState,
  MRT_SortingState,
  MRT_TableInstance,
  MRT_ColumnFiltersState,
  MRT_Updater,
} from "material-react-table";
import { useAuth } from "react-oidc-context";
import { User } from "oidc-client-ts";
import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import { useInspectionsData } from "@/hooks/useInspections";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useProjectsData } from "@/hooks/useProjects";
import { useInitiationsData } from "@/hooks/useInspections";
import { Inspection, InspectionGridQueryParams } from "@/models/Inspection";
import { cachedFiltersStore } from "@/store/cachedFiltersStore";
import { IRProgressEnumText, InspectionStatusEnum, STAFF_USER_POSITION } from "@/utils/constants";
import { Box, CircularProgress, Typography } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import Pagination from "@/components/Shared/Pagination";
import { useTableHandlers } from "@/components/Shared/MasterDataTable/useTableHandlers";
import {
  useConvertFiltersToQueryParams,
  useInspectionsGridColumns,
} from "@/components/App/Inspections/InspectionsGrid/InspectionsGridUtils";
import ShowOnlyMyInspectionsSwitch from "@/components/App/Inspections/InspectionsGrid/ShowOnlyMyInspectionsSwitch";
import InspectionsGridExport from "@/components/App/Inspections/InspectionsGrid/InspectionsGridExport";
import { AppConfig } from "@/utils/config";
import { StaffUser } from "@/models/Staff";

export const Route = createFileRoute(
  "/_authenticated/ce-database/inspections/"
)({ component: Inspections });

const inspectionsColumnFiltersCacheKey = "inspections-column-filters";

// Helper to get current staff from user and staff list
const getCurrentStaff = (currentUser: User | undefined | null, staffList: StaffUser[] | undefined) => {
  if (!currentUser?.profile?.preferred_username || !staffList) return null;
  return staffList.find(
    (staff) => staff.auth_user_guid === currentUser.profile.preferred_username
  );
};

// Helper to create default filters for a staff member
const createDefaultFilters = (staffId: string, defaultMyChecked: boolean): {
  externalFilters: Record<string, string[] | string>;
  columnFilters: MRT_ColumnFiltersState;
} => {
  if (defaultMyChecked) {
    return {
      externalFilters: {
        primary_officer_ids: [staffId],
      },
      columnFilters: [
        { id: "status", value: ["OPEN"] },
        {
          id: "primary_officer",
          value: [staffId],
        },
      ],
    }
  }
  return {
    externalFilters: {},
    columnFilters: [{ id: "status", value: ["OPEN"] }],
  };
}

export function Inspections() {
  const { data: projects } = useProjectsData();
  const { data: initiations } = useInitiationsData();
  const { isLoading: authLoading, user: currentUser } = useAuth();
  const { data: staffList, isLoading: staffLoading } = useStaffUsersData({ isActive: true, otherPositions: false });

  const irProgressOptions = useMemo(
    () =>
      Object.entries(IRProgressEnumText).map(([id, name]) => ({
        id,
        name,
      })),
    []
  );

  const inspectionStatusOptions = useMemo(
    () =>
      Object.entries(InspectionStatusEnum).map(([id, name]) => ({
        id,
        name,
      })),
    []
  );

  // Initialize state with functions to avoid re-computation
  const [myInspectionsChecked, setMyInspectionsChecked] = useState(false);
  const [sorting, setSorting] = useState<MRT_SortingState>(() => [
    { id: "start_date", desc: true },
  ]);

  const [pagination, setPagination] = useState(() => ({
    pageIndex: 0,
    pageSize: AppConfig.defaultPageSize,
  }));

  const [columnFilters, setColumnFilters] = useState<
    MRT_TableState<Inspection>["columnFilters"]
  >([]);
  
  const [globalFilter, setGlobalFilter] = useState<string>("");
  
  const [externalFilters, setExternalFilters] = useState<
    Record<string, string[] | string>
  >({});

  // Ref to track if filters have been initialized
  const filtersInitialized = useRef(false);
  const [isRestored, setIsRestored] = useState(false);

  // Get cached filters store methods
  const { getFilters, getExternalFilters, getSorting, hasHydrated } = cachedFiltersStore();

  const cachedColumnFilters = getFilters(inspectionsColumnFiltersCacheKey);
  const cachedExternalFilters = getExternalFilters(inspectionsColumnFiltersCacheKey);
  const cachedSorting = getSorting(inspectionsColumnFiltersCacheKey);

  const currentStaff = useMemo(() => {
    return getCurrentStaff(currentUser, staffList);
  }, [currentUser, staffList]);

  // Initialization effect
  useEffect(() => {
    // Don't initialize if already done, or if it isn't loaded yet
    if (!hasHydrated || filtersInitialized.current || authLoading || staffLoading || !currentStaff) {
      return;
    }

    filtersInitialized.current = true;

    const hasCache =
      (Array.isArray(cachedColumnFilters) &&
        cachedColumnFilters.length > 0) ||
      (cachedExternalFilters &&
        Object.keys(cachedExternalFilters).length > 0) ||
      (cachedSorting &&
        Array.isArray(cachedSorting) &&
        cachedSorting.length > 0);

    if (hasCache) {
      // Restore from cache
      if (cachedColumnFilters.length > 0) {
        setColumnFilters(cachedColumnFilters);
      }
      
      if (cachedExternalFilters) {
        const restored = cachedExternalFilters as Record<string, string[] | string>;
        setExternalFilters(restored);

        if (restored.globalFilter) {
          setGlobalFilter(restored.globalFilter as string);
        }

        // Restore switch state
        if (restored.myInspectionsChecked !== undefined) {
          setMyInspectionsChecked(Boolean(restored.myInspectionsChecked));
        } else {
          // Get from primary_officer filter
          const primaryOfficer = restored.primary_officer_ids;
          const derivedState =
            Array.isArray(primaryOfficer) &&
            primaryOfficer.some((id) => Boolean(id));
          setMyInspectionsChecked(derivedState);
        }
      }

      if (cachedSorting && Array.isArray(cachedSorting) && cachedSorting.length > 0) {
        if (cachedSorting[0]?.id) {
          setSorting(cachedSorting);
        }
      }
    } else {
      // Apply defaults for first-time users
      const officerPositions = [
        STAFF_USER_POSITION.OFFICER,
        STAFF_USER_POSITION.SENIOR_OFFICER,
      ];

      const defaultChecked = Boolean(currentStaff.position_id && 
        officerPositions.includes(currentStaff.position_id));
      const defaults = createDefaultFilters(currentStaff.id.toString(), defaultChecked);
      setExternalFilters(defaults.externalFilters);
      setColumnFilters(defaults.columnFilters);
      setMyInspectionsChecked(defaultChecked);
    }

    setIsRestored(true);
  }, [authLoading, staffLoading, currentStaff, cachedColumnFilters, cachedExternalFilters, cachedSorting, hasHydrated]);

  // Debounced cache persistence - only after initialization
  const cacheTimeoutRef = useRef<NodeJS.Timeout>();
  
  useEffect(() => {
    // Only cache after filters are initialized
    if (!filtersInitialized.current || !isRestored) return;

    // Clear previous timeout
    if (cacheTimeoutRef.current) {
      clearTimeout(cacheTimeoutRef.current);
    }

    // Debounce cache updates to reduce write frequency
    cacheTimeoutRef.current = setTimeout(() => {
      cachedFiltersStore.getState().setFilters(
        inspectionsColumnFiltersCacheKey,
        columnFilters,
        {
          ...externalFilters,
          globalFilter,
          myInspectionsChecked,
        },
        sorting
      );
    }, 300); // 300ms debounce

    return () => {
      if (cacheTimeoutRef.current) {
        clearTimeout(cacheTimeoutRef.current);
      }
    };
  }, [columnFilters, externalFilters, globalFilter, sorting, myInspectionsChecked, isRestored]);

  // Call custom hooks at top level
  const convertFiltersToQueryParams = useConvertFiltersToQueryParams(externalFilters);

  const queryParams: InspectionGridQueryParams = useMemo(() => {
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

  // Fetch data
  const { data, isLoading } = useInspectionsData(queryParams);
  
  const inspectionsList = useMemo(() => data?.items ?? [], [data?.items]);

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

  // Column filter handler that enforces "My Inspections" toggle
  const handleColumnFiltersChange = useCallback(
    (updater: MRT_Updater<MRT_ColumnFiltersState>) => {
      setColumnFilters((prevFilters) => {
        const newFilters = typeof updater === 'function' ? updater(prevFilters) : updater;
        
        // If "My Inspections" is checked, ensure primary_officer filter is present
        if (myInspectionsChecked && currentStaff) {
          const hasPrimaryOfficerFilter = newFilters.some(
            (filter) => filter.id === "primary_officer"
          );
          
          if (!hasPrimaryOfficerFilter) {
            const primaryOfficerFilter = {
              id: "primary_officer",
              value: [currentStaff.id.toString()],
            };
            return [...newFilters, primaryOfficerFilter];
          }
        }
        
        return newFilters;
      });
    },
    [currentStaff, myInspectionsChecked]
  );

  // Optimize My Inspections switch handler
  const handleMyInspectionsSwitchChange = useCallback(
    (filters: {
      checked: boolean;
      externalFilters: Record<string, string[] | string>;
      columnFilters?: MRT_TableState<Inspection>["columnFilters"];
    }) => {
      setMyInspectionsChecked(filters.checked);
      setExternalFilters(filters.externalFilters);
      setPagination((prev) => ({ ...prev, pageIndex: 0 }));

      // Update column filters if provided
      if (filters.columnFilters !== undefined) {
        if (filters.checked) {
          setColumnFilters((prevFilters) => {
            const filtered = prevFilters.filter(
              (filter) => filter.id !== "primary_officer"
            );
            return [...filtered, ...filters.columnFilters!];
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

  const columns = useInspectionsGridColumns({
    projectList: projects,
    initiationList: initiations,
    irProgressList: irProgressOptions,
    staffUserList: staffList,
    inspectionStatusList: inspectionStatusOptions,
  });

  // Show loading state during initialization
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
      data={inspectionsList}
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
        tableTitle: "Inspections",
      }}
      enableSorting={true}
      enablePagination={false}
      hideFilterToggle={true}
      renderTopToolbarCustomActions={({
        table,
      }: {
        table: MRT_TableInstance<Inspection>;
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
              Inspections
            </Typography>
            <ShowOnlyMyInspectionsSwitch
              staffUsers={staffList ?? []}
              onFiltersChange={handleMyInspectionsSwitchChange}
              initialChecked={myInspectionsChecked}
            />
          </Box>

          {/* Pagination and controls section */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              width: "100%",
            }}
          >
            {/* Left side - Export and Pagination */}
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <InspectionsGridExport queryParams={queryParams} />
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
