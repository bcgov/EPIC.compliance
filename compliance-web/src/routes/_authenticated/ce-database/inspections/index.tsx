import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import { useInspectionsData } from "@/hooks/useInspections";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useProjectsData } from "@/hooks/useProjects";
import { useInitiationsData } from "@/hooks/useInspections";
import { Inspection, InspectionGridQueryParams } from "@/models/Inspection";
import { cachedFiltersStore } from "@/store/cachedFiltersStore";
import { IRProgressEnumText, InspectionStatusEnum } from "@/utils/constants";
import { Box, CircularProgress, Typography } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import {
  MRT_TableState,
  MRT_SortingState,
  MRT_TableInstance,
} from "material-react-table";
import { useEffect, useMemo, useState, useRef, useCallback } from "react";
import { useAuth } from "react-oidc-context";
import InspectionsGridPagination from "@/components/App/Inspections/InspectionsGrid/InspectionsGridPagination";
import { useTableHandlers } from "@/components/Shared/MasterDataTable/useTableHandlers";
import {
  useConvertFiltersToQueryParams,
  useInspectionsGridColumns,
} from "@/components/App/Inspections/InspectionsGrid/InspectionsGridUtils";
import ShowOnlyMyInspectionsSwitch from "@/components/App/Inspections/InspectionsGrid/ShowOnlyMyInspectionsSwitch";
import InspectionsGridExport from "@/components/App/Inspections/InspectionsGrid/InspectionsGridExport";
import { AppConfig } from "@/utils/config";

export const Route = createFileRoute(
  "/_authenticated/ce-database/inspections/"
)({ component: Inspections });

const inspectionsColumnFiltersCacheKey = "inspections-column-filters";

export function Inspections() {
  const { data: projects } = useProjectsData();
  const { data: initiations } = useInitiationsData();
  const { isLoading: authLoading, user: currentUser } = useAuth();
  const { data: staffList, isLoading: staffLoading } = useStaffUsersData();
  // State for "My Inspections" switch - default to true for first-time users
  const [myInspectionsChecked, setMyInspectionsChecked] = useState(true);
  const [sorting, setSorting] = useState<MRT_SortingState>([
    { id: "ir_number", desc: false },
  ]);

  // Create static data for IR Progress and Inspection Status
  const irProgressOptions = Object.entries(IRProgressEnumText).map(
    ([id, name]) => ({
      id,
      name,
    })
  );

  const inspectionStatusOptions = Object.entries(InspectionStatusEnum).map(
    ([id, name]) => ({
      id,
      name,
    })
  );

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: AppConfig.defaultPageSize,
  });

  const [columnFilters, setColumnFilters] = useState<
    MRT_TableState<Inspection>["columnFilters"]
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
    columnFilters: MRT_TableState<Inspection>["columnFilters"];
    externalFilters: Record<string, string[] | string>;
    globalFilter: string;
    sorting: MRT_SortingState;
    myInspectionsChecked: boolean;
  }>({
    columnFilters: [],
    externalFilters: {},
    globalFilter: "",
    sorting: [{ id: "ir_number", desc: false }],
    myInspectionsChecked: true, // Default to true for first-time users
  });

  // Get cached filters store methods
  const { getFilters, getExternalFilters, getSorting } = cachedFiltersStore();
  const cachedColumnFilters = getFilters(inspectionsColumnFiltersCacheKey);
  const cachedExternalFilters = getExternalFilters(
    inspectionsColumnFiltersCacheKey
  );
  const cachedSorting = getSorting(inspectionsColumnFiltersCacheKey);

  // Find current user from staff list

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

      // Restore "My Inspections" switch state if it was cached
      if (restoredExternalFilters.myInspectionsChecked !== undefined) {
        // Use the explicitly stored switch state
        const restoredSwitchState = Boolean(
          restoredExternalFilters.myInspectionsChecked
        );
        setMyInspectionsChecked(restoredSwitchState);

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
          restoredExternalFilters.primary_officer_ids || [];
        const derivedSwitchState = !!(primaryOfficerFilter?.length > 0);
        setMyInspectionsChecked(derivedSwitchState);

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
    } else {
      // No cached filters - apply default "My Inspections" filter for first-time users
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
              id: "primary_officer",
              value: [currentStaff.id.toString()],
            },
          ];

          setExternalFilters(defaultExternalFilters);
          setColumnFilters(defaultColumnFilters);
          setMyInspectionsChecked(true);

          // Update prevFilters to prevent unnecessary caching during initial setup
          prevFilters.current = {
            ...prevFilters.current,
            externalFilters: defaultExternalFilters,
            columnFilters: defaultColumnFilters,
            myInspectionsChecked: true,
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
        myInspectionsChecked,
      };

      const hasChanged =
        JSON.stringify(currentFilters) !== JSON.stringify(prevFilters.current);

      if (hasChanged) {
        cachedFiltersStore.getState().setFilters(
          inspectionsColumnFiltersCacheKey,
          columnFilters,
          {
            ...externalFilters,
            globalFilter,
            myInspectionsChecked, // Store the switch state explicitly
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
    myInspectionsChecked,
  ]);

  // Use the extracted utility function
  const convertFiltersToQueryParams =
    useConvertFiltersToQueryParams(externalFilters);

  const queryParams: InspectionGridQueryParams = useMemo(() => {
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

  const { data, isLoading } = useInspectionsData(queryParams);
  const inspectionsList = useMemo(() => data?.items ?? [], [data]);

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

  // Handle "My Inspections" switch changes
  const handleMyInspectionsSwitchChange = useCallback(
    (filters: {
      checked: boolean;
      externalFilters: Record<string, string[] | string>;
      columnFilters?: MRT_TableState<Inspection>["columnFilters"];
    }) => {
      // Only update if the values have actually changed
      const filtersChanged =
        JSON.stringify(filters.externalFilters) !==
        JSON.stringify(externalFilters);
      const checkedChanged = filters.checked !== myInspectionsChecked;

      if (checkedChanged) {
        setMyInspectionsChecked(filters.checked);
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
    [externalFilters, handleColumnFiltersChange, myInspectionsChecked]
  );

  // Use the extracted utility function for columns
  const columns = useInspectionsGridColumns({
    projectList: projects,
    initiationList: initiations,
    irProgressList: irProgressOptions,
    staffUserList: staffList,
    inspectionStatusList: inspectionStatusOptions,
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
      data={inspectionsList ?? []}
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
              <InspectionsGridPagination
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
