import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import { useComplaintsData } from "@/hooks/useComplaints";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useProjectsData } from "@/hooks/useProjects";
import { useTopicsData } from "@/hooks/useTopics";
import { useComplaintSourcesData } from "@/hooks/useComplaints";
import { Complaint, ComplaintGridQueryParams } from "@/models/Complaint";
import { cachedFiltersStore } from "@/store/cachedFiltersStore";
import { Box, CircularProgress, Typography } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import { MRT_TableState, MRT_SortingState } from "material-react-table";
import { useCallback, useEffect, useMemo, useState, useRef } from "react";
import { useAuth } from "react-oidc-context";
import ComplaintsGridPagination from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridPagination";
import {
  useConvertFiltersToQueryParams,
  useComplaintsGridColumns,
} from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridUtils";
import ComplaintsGridExport from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridExport";
import ShowOnlyMyComplaintsSwitch from "@/components/App/Complaints/ComplaintsGrid/ShowOnlyMyComplaintsSwitch";
import { AppConfig } from "@/utils/config";

export const Route = createFileRoute(
  "/_authenticated/ce-database/complaints/"
)({ component: Complaints });

const complaintsColumnFiltersCacheKey = "complaints-column-filters";

export function Complaints() {
  const { data: projects } = useProjectsData();
  const { data: topics } = useTopicsData();
  const { data: complaintSources } = useComplaintSourcesData();
  const { data: staffList, isLoading: staffLoading } = useStaffUsersData();
  const { isLoading: authLoading } = useAuth();
  const [sorting, setSorting] = useState<MRT_SortingState>([
    { id: "complaint_number", desc: false },
  ]);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: AppConfig.defaultPageSize,
  });

  const [columnFilters, setColumnFilters] = useState<
    MRT_TableState<Complaint>["columnFilters"]
  >([]);
  const [globalFilter, setGlobalFilter] = useState<string>("");
  const [externalFilters, setExternalFilters] = useState<
    Record<string, string[] | string>
  >({});

  // State for "My Files" switch
  const [myFilesChecked, setMyFilesChecked] = useState(false);

  // Track if we're in the initial load phase to prevent caching during restoration
  const isInitialLoad = useRef(true);
  const [isRestored, setIsRestored] = useState(false);

  // Track previous values to prevent unnecessary caching
  const prevFilters = useRef<{
    columnFilters: MRT_TableState<Complaint>["columnFilters"];
    externalFilters: Record<string, string[] | string>;
    globalFilter: string;
    sorting: MRT_SortingState;
    myFilesChecked: boolean;
  }>({
    columnFilters: [],
    externalFilters: {},
    globalFilter: "",
    sorting: [{ id: "complaint_number", desc: false }],
    myFilesChecked: false,
  });

  // Get cached filters store methods
  const { getFilters, getExternalFilters, getSorting } = cachedFiltersStore();
  const cachedColumnFilters = getFilters(complaintsColumnFiltersCacheKey);
  const cachedExternalFilters = getExternalFilters(
    complaintsColumnFiltersCacheKey
  );
  const cachedSorting = getSorting(complaintsColumnFiltersCacheKey);

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

      // Restore global filter if it was cached
      if (restoredExternalFilters.globalFilter) {
        setGlobalFilter(restoredExternalFilters.globalFilter as string);
      }

      // Restore "My Files" switch state if it was cached
      if (restoredExternalFilters.primary_officer_id && 
          Array.isArray(restoredExternalFilters.primary_officer_id) && 
          restoredExternalFilters.primary_officer_id.length > 0) {
        setMyFilesChecked(true);
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
  }, [cachedColumnFilters, cachedExternalFilters, cachedSorting]);

  // Cache all filters when they change (but not during initial load)
  useEffect(() => {
    if (!isInitialLoad.current) {
      // Check if any values have actually changed
      const currentFilters = {
        columnFilters,
        externalFilters,
        globalFilter,
        sorting,
        myFilesChecked,
      };

      const hasChanged =
        JSON.stringify(currentFilters) !== JSON.stringify(prevFilters.current);

      if (hasChanged) {
        cachedFiltersStore.getState().setFilters(
          complaintsColumnFiltersCacheKey,
          columnFilters,
          {
            ...externalFilters,
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
    globalFilter,
    sorting,
    myFilesChecked,
  ]);

  // Use the extracted utility function
  const convertFiltersToQueryParams =
    useConvertFiltersToQueryParams(externalFilters);

  const queryParams: ComplaintGridQueryParams = useMemo(() => {
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

  const { data, isLoading } = useComplaintsData(queryParams);
  const complaintsList = useMemo(() => data?.items ?? [], [data]);

  const handlePaginationChange = useCallback(
    (
      updater:
        | MRT_TableState<Complaint>["pagination"]
        | ((
            old: MRT_TableState<Complaint>["pagination"]
          ) => MRT_TableState<Complaint>["pagination"])
    ) => {
      setPagination(updater);
    },
    []
  );

  const handleSortingChange = useCallback(
    (
      updater: MRT_SortingState | ((old: MRT_SortingState) => MRT_SortingState)
    ) => {
      const newSorting =
        typeof updater === "function" ? updater(sorting) : updater;

      // Only reset pagination if sorting actually changed
      const sortingChanged =
        JSON.stringify(newSorting) !== JSON.stringify(sorting);

      setSorting(updater);

      if (sortingChanged) {
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
      }
    },
    [sorting]
  );

  const handleColumnFiltersChange = useCallback(
    (
      updater:
        | MRT_TableState<Complaint>["columnFilters"]
        | ((
            old: MRT_TableState<Complaint>["columnFilters"]
          ) => MRT_TableState<Complaint>["columnFilters"])
    ) => {
      const newFilters =
        typeof updater === "function" ? updater(columnFilters) : updater;

      // Only reset pagination if filters actually changed
      const filtersChanged =
        JSON.stringify(newFilters) !== JSON.stringify(columnFilters);

      setColumnFilters(updater);

      if (filtersChanged) {
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
      }
    },
    [columnFilters]
  );

  const handleGlobalFilterChange = useCallback(
    (
      updater:
        | MRT_TableState<Complaint>["globalFilter"]
        | ((
            old: MRT_TableState<Complaint>["globalFilter"]
          ) => MRT_TableState<Complaint>["globalFilter"])
    ) => {
      const newGlobalFilter =
        typeof updater === "function" ? updater(globalFilter) : updater;

      // Only reset pagination if global filter actually changed
      const globalFilterChanged = newGlobalFilter !== globalFilter;

      setGlobalFilter(updater);

      if (globalFilterChanged) {
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
      }
    },
    [globalFilter]
  );

  // Handle "My Files" switch changes
  const handleMyFilesSwitchChange = useCallback(
    (filters: {
      checked: boolean;
      externalFilters: Record<string, string[] | string>;
      columnFilters?: MRT_TableState<Complaint>["columnFilters"];
    }) => {
      setMyFilesChecked(filters.checked);
      setExternalFilters(filters.externalFilters);
      
      // Reset pagination when filters change
      setPagination((prev) => ({ ...prev, pageIndex: 0 }));
    },
    []
  );

  // Use the extracted utility function for columns
  const columns = useComplaintsGridColumns({
    projectList: projects,
    topicList: topics,
    complaintSourceList: complaintSources,
    staffUserList: staffList,
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
      data={complaintsList ?? []}
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
        tableTitle: "Complaints",
      }}
      enableSorting={true}
      enablePagination={false}
      hideFilterToggle={true}
      renderTopToolbarCustomActions={({ table }) => (
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
              onFiltersChange={handleMyFilesSwitchChange}
              onColumnFiltersChange={handleColumnFiltersChange}
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
              <ComplaintsGridPagination
                table={table}
                totalCount={data?.total || 0}
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
