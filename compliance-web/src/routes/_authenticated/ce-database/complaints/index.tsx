import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import {
  useComplaintResolutionsData,
  useComplaintsData,
} from "@/hooks/useComplaints";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useCurrentStaffUser } from "@/hooks/useAuthorization";
import { useProjectsData } from "@/hooks/useProjects";
import { useTopicsData } from "@/hooks/useTopics";
import { useComplaintSourcesData } from "@/hooks/useComplaints";
import { Complaint, ComplaintGridQueryParams } from "@/models/Complaint";
import { cachedFiltersStore } from "@/store/cachedFiltersStore";
import { Box, CircularProgress, Typography } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import {
  MRT_TableState,
  MRT_SortingState,
  MRT_TableInstance,
  MRT_ColumnFiltersState,
  MRT_Updater,
} from "material-react-table";
import { useCallback, useEffect, useMemo, useState, useRef } from "react";
import { useAuth } from "react-oidc-context";
import Pagination from "@/components/Shared/Pagination";
import { useTableHandlers } from "@/components/Shared/MasterDataTable/useTableHandlers";
import {
  useConvertFiltersToQueryParams,
  useComplaintsGridColumns,
} from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridUtils";
import ComplaintsGridExport from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridExport";
import ShowOnlyMyComplaintsSwitch from "@/components/App/Complaints/ComplaintsGrid/ShowOnlyMyComplaintsSwitch";
import { AppConfig } from "@/utils/config";
import { ComplaintStatusEnum, STAFF_USER_POSITION } from "@/utils/constants";

export const Route = createFileRoute("/_authenticated/ce-database/complaints/")(
  { component: Complaints }
);

const complaintsColumnFiltersCacheKey = "complaints-column-filters";

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
        { id: "status", value: [ComplaintStatusEnum.OPEN] },
        {
          id: "primary_officer_ids",
          value: [staffId],
        },
      ],
    }
  }
  return {
    externalFilters: {},
    columnFilters: [{ id: "status", value: [ComplaintStatusEnum.OPEN] }],
  };
}

export function Complaints() {
  const { data: projects } = useProjectsData();
  const { data: topics } = useTopicsData();
  const { data: complaintSources } = useComplaintSourcesData();
  const { data: complaintResolutions } = useComplaintResolutionsData();
  const { data: staffList, isLoading: staffLoading } = useStaffUsersData({ isActive: true, otherPositions: false });
  const { isLoading: authLoading } = useAuth();
  const { currentStaff, isLoading: currentStaffLoading } = useCurrentStaffUser();

  const [sorting, setSorting] = useState<MRT_SortingState>(() => [
    { id: "date_received", desc: true },
  ]);

  const [pagination, setPagination] = useState(() => ({
    pageIndex: 0,
    pageSize: AppConfig.defaultPageSize,
  }));

  const [columnFilters, setColumnFilters] = useState<
    MRT_TableState<Complaint>["columnFilters"]
  >([]);
  
  const [globalFilter, setGlobalFilter] = useState<string>("");
  
  const [externalFilters, setExternalFilters] = useState<
    Record<string, string[] | string>
  >({});

  const [myFilesChecked, setMyFilesChecked] = useState(false);
  
  // Ref to track if filters have been initialized
  const filtersInitialized = useRef(false);
  const [isRestored, setIsRestored] = useState(false);

  // Get cached filters store methods
  const { getFilters, getExternalFilters, getSorting, hasHydrated } = cachedFiltersStore();

  const cachedColumnFilters = getFilters(complaintsColumnFiltersCacheKey);
  const cachedExternalFilters = getExternalFilters(complaintsColumnFiltersCacheKey);
  const cachedSorting = getSorting(complaintsColumnFiltersCacheKey);


  useEffect(() => {
    // Don't initialize if already done, or if it isn't loaded yet
    if (!hasHydrated || filtersInitialized.current || authLoading || currentStaffLoading || !currentStaff) {
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
      const restored = (cachedExternalFilters ?? {}) as Record<
        string,
        string[] | string
      >;

      if (restored.globalFilter) {
        setGlobalFilter(restored.globalFilter as string);
      }

      // The toggle is the source of truth for the "my complaints" filter.
      let restoredMyChecked: boolean;
      if (restored.myFilesChecked !== undefined) {
        restoredMyChecked = Boolean(restored.myFilesChecked);
      } else {
        // Derive from the cached primary_officer filter (legacy cache)
        const primaryOfficer = restored.primary_officer_ids;
        restoredMyChecked =
          Array.isArray(primaryOfficer) &&
          primaryOfficer.some((id) => Boolean(id));
      }
      setMyFilesChecked(restoredMyChecked);

      // Reconcile the cached filters with the toggle so they can never disagree.
      const staffId = currentStaff.id.toString();
      const baseColumnFilters = cachedColumnFilters.filter(
        (f) => f.id !== "primary_officer_ids"
      );
      const baseExternalFilters: Record<string, string[] | string> = {
        ...restored,
      };
      delete baseExternalFilters.primary_officer_ids;

      if (restoredMyChecked) {
        setColumnFilters([
          ...baseColumnFilters,
          { id: "primary_officer_ids", value: [staffId] },
        ]);
        setExternalFilters({
          ...baseExternalFilters,
          primary_officer_ids: [staffId],
        });
      } else {
        setColumnFilters(baseColumnFilters);
        setExternalFilters(baseExternalFilters);
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
      setMyFilesChecked(defaultChecked);
    }

    setIsRestored(true);
  }, [authLoading, currentStaffLoading, currentStaff, cachedColumnFilters, cachedExternalFilters, cachedSorting, hasHydrated]);

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
        complaintsColumnFiltersCacheKey,
        columnFilters,
        {
          ...externalFilters,
          globalFilter,
          myFilesChecked,
        },
        sorting
      );
    }, 300); // 300ms debounce

    return () => {
      if (cacheTimeoutRef.current) {
        clearTimeout(cacheTimeoutRef.current);
      }
    };
  }, [columnFilters, externalFilters, globalFilter, sorting, myFilesChecked, isRestored]);

  const convertFiltersToQueryParams = useConvertFiltersToQueryParams(externalFilters);

  const queryParams: ComplaintGridQueryParams = useMemo(() => {
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

  // Get data
  const { data, isLoading } = useComplaintsData(queryParams);
  
  const complaintsList = useMemo(() => data?.items ?? [], [data?.items]);

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

  // Column filter handler that enforces "My Files" toggle
  const handleColumnFiltersChange = useCallback(
    (updater: MRT_Updater<MRT_ColumnFiltersState>) => {
      setColumnFilters((prevFilters) => {
        const newFilters = typeof updater === 'function' ? updater(prevFilters) : updater;
        
        // If "My Files" is checked, ensure primary_officer_ids filter is present
        if (myFilesChecked && currentStaff) {
          const hasPrimaryOfficerFilter = newFilters.some(
            (filter) => filter.id === "primary_officer_ids"
          );
          
          // If user removed the primary_officer_ids filter, re-add it
          if (!hasPrimaryOfficerFilter) {
            const primaryOfficerFilter = {
              id: "primary_officer_ids",
              value: [currentStaff.id.toString()],
            };
            return [...newFilters, primaryOfficerFilter];
          }
        }
        
        return newFilters;
      });
    },
    [myFilesChecked, currentStaff]
  );

  const handleMyFilesSwitchChange = useCallback(
    (filters: {
      checked: boolean;
      externalFilters: Record<string, string[] | string>;
      columnFilters?: MRT_TableState<Complaint>["columnFilters"];
    }) => {
      // Batch state updates
      setMyFilesChecked(filters.checked);
      setExternalFilters(filters.externalFilters);
      setPagination((prev) => ({ ...prev, pageIndex: 0 }));

      // Update column filters if provided
      if (filters.columnFilters !== undefined) {
        if (filters.checked) {
          setColumnFilters((prevFilters) => {
            const filtered = prevFilters.filter(
              (filter) => filter.id !== "primary_officer_ids"
            );
            return [...filtered, ...filters.columnFilters!];
          });
        } else {
          setColumnFilters((prevFilters) =>
            prevFilters.filter((filter) => filter.id !== "primary_officer_ids")
          );
        }
      }
    },
    []
  );

  const columns = useComplaintsGridColumns({
    projectList: projects,
    topicList: topics,
    complaintSourceList: complaintSources,
    staffUserList: staffList,
    complaintResolutionList: complaintResolutions,
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
      data={complaintsList}
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
        tableTitle: "Complaints",
      }}
      enableSorting={true}
      enablePagination={false}
      hideFilterToggle={true}
      renderTopToolbarCustomActions={({
        table,
      }: {
        table: MRT_TableInstance<Complaint>;
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
              Complaints
            </Typography>
            <ShowOnlyMyComplaintsSwitch
              staffUsers={staffList ?? []}
              onFiltersChange={handleMyFilesSwitchChange}
              initialChecked={myFilesChecked}
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
              <ComplaintsGridExport queryParams={queryParams} />
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
