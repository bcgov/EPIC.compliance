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
} from "material-react-table";
import { useCallback, useEffect, useMemo, useState, useRef } from "react";
import { useAuth } from "react-oidc-context";
import ComplaintsGridPagination from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridPagination";
import { useTableHandlers } from "@/components/Shared/MasterDataTable/useTableHandlers";
import {
  useConvertFiltersToQueryParams,
  useComplaintsGridColumns,
} from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridUtils";
import ComplaintsGridExport from "@/components/App/Complaints/ComplaintsGrid/ComplaintsGridExport";
import ShowOnlyMyComplaintsSwitch from "@/components/App/Complaints/ComplaintsGrid/ShowOnlyMyComplaintsSwitch";
import { AppConfig } from "@/utils/config";

export const Route = createFileRoute("/_authenticated/ce-database/complaints/")(
  { component: Complaints }
);

const complaintsColumnFiltersCacheKey = "complaints-column-filters";

export function Complaints() {
  const { data: projects } = useProjectsData();
  const { data: topics } = useTopicsData();
  const { data: complaintSources } = useComplaintSourcesData();
  const { data: complaintResolutions } = useComplaintResolutionsData();
  const { data: staffList, isLoading: staffLoading } = useStaffUsersData();
  const { user: currentUser, isLoading: authLoading } = useAuth();
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

  // State for "My Files" switch - default to true for first-time users
  const [myFilesChecked, setMyFilesChecked] = useState(true);

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
    myFilesChecked: true, // Default to true for first-time users
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
      if (restoredExternalFilters.myFilesChecked !== undefined) {
        // Use the explicitly stored switch state
        const restoredSwitchState = Boolean(
          restoredExternalFilters.myFilesChecked
        );
        setMyFilesChecked(restoredSwitchState);

        // If switch is ON, ensure column filters are set up for UI display
        if (
          restoredSwitchState &&
          currentUser?.profile?.preferred_username &&
          staffList
        ) {
          const currentStaff = staffList.find(
            (staff) =>
              staff.auth_user_guid === currentUser.profile.preferred_username
          );
          if (currentStaff) {
            // Add primary_officer_ids column filter for UI display
            const primaryOfficerColumnFilter = {
              id: "primary_officer_ids",
              value: [currentStaff.id.toString()],
            };
            setColumnFilters((prev) => {
              const filtered = prev.filter(
                (filter) => filter.id !== "primary_officer_ids"
              );
              return [...filtered, primaryOfficerColumnFilter];
            });
          }
        }
      } else {
        // Fallback: derive from primary_officer filter if switch state not stored
        const primaryOfficerFilter =
          restoredExternalFilters.primary_officer_ids || [];
        const derivedSwitchState = !!(primaryOfficerFilter?.length > 0);
        setMyFilesChecked(derivedSwitchState);

        // If derived state is ON, ensure column filters are set up
        if (
          derivedSwitchState &&
          currentUser?.profile?.preferred_username &&
          staffList
        ) {
          const currentStaff = staffList.find(
            (staff) =>
              staff.auth_user_guid === currentUser.profile.preferred_username
          );
          if (currentStaff) {
            // Add primary_officer_ids column filter for UI display
            const primaryOfficerColumnFilter = {
              id: "primary_officer_ids",
              value: [currentStaff.id.toString()],
            };
            setColumnFilters((prev) => {
              const filtered = prev.filter(
                (filter) => filter.id !== "primary_officer_ids"
              );
              return [...filtered, primaryOfficerColumnFilter];
            });
          }
        }
      }
    } else {
      // No cached filters - apply default "My Files" filter for first-time users
      if (currentUser?.profile?.preferred_username && staffList) {
        const currentStaff = staffList.find(
          (staff) =>
            staff.auth_user_guid === currentUser.profile.preferred_username
        );
        if (currentStaff) {
          const defaultExternalFilters = {
            primary_officer_ids: [currentStaff.id.toString()],
          };
          const defaultColumnFilters = [
            {
              id: "primary_officer_ids",
              value: [currentStaff.id.toString()],
            },
          ];

          setExternalFilters(defaultExternalFilters);
          setColumnFilters(defaultColumnFilters);
          setMyFilesChecked(true);

          // Update prevFilters to prevent unnecessary caching during initial setup
          prevFilters.current = {
            ...prevFilters.current,
            externalFilters: defaultExternalFilters,
            columnFilters: defaultColumnFilters,
            myFilesChecked: true,
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
    staffList,
    currentUser,
  ]);

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
            myFilesChecked, // Store the switch state explicitly
          },
          sorting
        );

        // Update previous values
        prevFilters.current = currentFilters;
      }
    }
  }, [columnFilters, externalFilters, globalFilter, sorting, myFilesChecked]);

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

  // Handle "My Files" switch changes
  const handleMyFilesSwitchChange = useCallback(
    (filters: {
      checked: boolean;
      externalFilters: Record<string, string[] | string>;
      columnFilters?: MRT_TableState<Complaint>["columnFilters"];
    }) => {
      // Only update if the values have actually changed
      const filtersChanged =
        JSON.stringify(filters.externalFilters) !==
        JSON.stringify(externalFilters);
      const checkedChanged = filters.checked !== myFilesChecked;

      if (checkedChanged) {
        setMyFilesChecked(filters.checked);
      }

      if (filtersChanged) {
        setExternalFilters(filters.externalFilters);
        // Reset pagination when filters change
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
      }

      // Update column filters if provided
      if (filters.columnFilters !== undefined) {
        if (filters.checked) {
          // When turning ON, merge with existing filters, replacing primary_officer_ids if it exists
          setColumnFilters((prevFilters) => {
            const filteredFilters = prevFilters.filter(
              (filter) => filter.id !== "primary_officer_ids"
            );
            return [...filteredFilters, ...filters.columnFilters!];
          });
        } else {
          // When turning OFF, remove primary_officer_ids filter but keep others
          setColumnFilters((prevFilters) => {
            return prevFilters.filter(
              (filter) => filter.id !== "primary_officer_ids"
            );
          });
        }
      }
    },
    [externalFilters, myFilesChecked]
  );

  // Use the extracted utility function for columns
  const columns = useComplaintsGridColumns({
    projectList: projects,
    topicList: topics,
    complaintSourceList: complaintSources,
    staffUserList: staffList,
    complaintResolutionList: complaintResolutions,
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
