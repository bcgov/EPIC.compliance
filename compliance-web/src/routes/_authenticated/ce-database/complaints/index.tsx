import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import {
  useComplaintResolutionsData,
  useComplaintsData,
} from "@/hooks/useComplaints";
import { useStaffUsersData } from "@/hooks/useStaff";
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
import type { User } from "oidc-client-ts";
import Pagination from "@/components/Shared/Pagination";
import { useTableHandlers } from "@/components/Shared/MasterDataTable/useTableHandlers";
import {
  useConvertFiltersToQueryParams,
  useComplaintsGridColumns,
} from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridUtils";
import ComplaintsGridExport from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridExport";
import ShowOnlyMyComplaintsSwitch from "@/components/App/Complaints/ComplaintsGrid/ShowOnlyMyComplaintsSwitch";
import { AppConfig } from "@/utils/config";
import { StaffUser } from "@/models/Staff";

export const Route = createFileRoute("/_authenticated/ce-database/complaints/")(
  { component: Complaints }
);

const complaintsColumnFiltersCacheKey = "complaints-column-filters";

// Helper to get current staff from user and staff list
const getCurrentStaff = (currentUser: User | undefined | null, staffList: StaffUser[] | undefined) => {
  if (!currentUser?.profile?.preferred_username || !staffList) return null;
  return staffList.find(
    (staff) => staff.auth_user_guid === currentUser.profile.preferred_username
  );
};

// Helper to create default filters for a staff member
const createDefaultFilters = (staffId: string) => ({
  externalFilters: {
    primary_officer_ids: [staffId],
  },
  columnFilters: [
    {
      id: "primary_officer_ids",
      value: [staffId],
    },
  ],
});

export function Complaints() {
  const { data: projects } = useProjectsData();
  const { data: topics } = useTopicsData();
  const { data: complaintSources } = useComplaintSourcesData();
  const { data: complaintResolutions } = useComplaintResolutionsData();
  const { data: staffList, isLoading: staffLoading } = useStaffUsersData();
  const { user: currentUser, isLoading: authLoading } = useAuth();

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

  const [myFilesChecked, setMyFilesChecked] = useState(true);
  
  // Ref to track if filters have been initialized
  const filtersInitialized = useRef(false);
  const [isRestored, setIsRestored] = useState(false);

  // Get cached filters store methods
  const { getFilters, getExternalFilters, getSorting } = cachedFiltersStore();

  const cachedData = useMemo(() => {
    return {
      columnFilters: getFilters(complaintsColumnFiltersCacheKey),
      externalFilters: getExternalFilters(complaintsColumnFiltersCacheKey),
      sorting: getSorting(complaintsColumnFiltersCacheKey),
    };
  }, [getFilters, getExternalFilters, getSorting]);

  const currentStaff = useMemo(() => {
    return getCurrentStaff(currentUser, staffList);
  }, [currentUser, staffList]);

  useEffect(() => {
    // Don't initialize if already done, or if it isn't loaded yet
    if (filtersInitialized.current || authLoading || staffLoading || !currentStaff) {
      return;
    }

    filtersInitialized.current = true;

    const hasCache = cachedData.columnFilters.length > 0 || 
                     (cachedData.externalFilters && Object.keys(cachedData.externalFilters).length > 0);

    if (hasCache) {
      // Restore from cache
      if (cachedData.columnFilters.length > 0) {
        setColumnFilters(cachedData.columnFilters);
      }
      
      if (cachedData.externalFilters) {
        const restored = cachedData.externalFilters as Record<string, string[] | string>;
        setExternalFilters(restored);

        if (restored.globalFilter) {
          setGlobalFilter(restored.globalFilter as string);
        }

        if (restored.myFilesChecked !== undefined) {
          setMyFilesChecked(Boolean(restored.myFilesChecked));
        } else {
          // Get from primary officer filter
          const primaryOfficer = restored.primary_officer_ids || [];
          const derivedState = Array.isArray(primaryOfficer) && primaryOfficer.length > 0;
          setMyFilesChecked(derivedState);
        }
      }

      if (cachedData.sorting && Array.isArray(cachedData.sorting) && cachedData.sorting.length > 0) {
        if (cachedData.sorting[0]?.id) {
          setSorting(cachedData.sorting);
        }
      }
    } else {
      // Apply defaults for first-time users
      const defaults = createDefaultFilters(currentStaff.id.toString());
      setExternalFilters(defaults.externalFilters);
      setColumnFilters(defaults.columnFilters);
      setMyFilesChecked(true);
    }

    setIsRestored(true);
  }, [authLoading, staffLoading, currentStaff, cachedData]);

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
