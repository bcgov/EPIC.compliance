import CaseFileDrawer from "@/components/App/CaseFiles/CaseFileDrawer";
import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import { KC_USER_GROUPS, useIsRolesAllowed } from "@/hooks/useAuthorization";
import { useCaseFilesData } from "@/hooks/useCaseFiles";
import { useProjectsData } from "@/hooks/useProjects";
import { useInitiationsData } from "@/hooks/useCaseFiles";
import { useStaffUsersData } from "@/hooks/useStaff";
import { CaseFile, CaseFileGridQueryParams } from "@/models/CaseFile";
import { cachedFiltersStore } from "@/store/cachedFiltersStore";
import { useDrawer } from "@/store/drawerStore";
import { notify } from "@/store/snackbarStore";
import { DRAWER_WIDTHS } from "@/utils/constants";
import { AppConfig } from "@/utils/config";
import { Box, Button, CircularProgress, Typography } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import { MRT_TableState, MRT_SortingState } from "material-react-table";
import { useCallback, useEffect, useMemo, useState, useRef } from "react";
import { useAuth } from "react-oidc-context";
import CaseFileGridPagination from "@/components/App/CaseFiles/CaseFileGrid/CaseFileGridPagination";
import {
  useConvertFiltersToQueryParams,
  useCaseFileGridColumns,
} from "@/components/App/CaseFiles/CaseFileGrid/CaseFileGridUtils";
import CaseFileGridExport from "@/components/App/CaseFiles/CaseFileGrid/CaseFileGridExport";
import ShowOnlyMyCaseFilesSwitch from "@/components/App/CaseFiles/CaseFileGrid/ShowOnlyMyCaseFilesSwitch";
import { AddRounded } from "@mui/icons-material";

export const Route = createFileRoute("/_authenticated/ce-database/case-files/")(
  {
    component: CaseFiles,
  }
);

const caseFilesColumnFiltersCacheKey = "case-files-column-filters";

export function CaseFiles() {
  const { data: projects } = useProjectsData();
  const { data: initiations } = useInitiationsData();
  const { data: staffList, isLoading: staffLoading } = useStaffUsersData();
  const { user: currentUser, isLoading: authLoading } = useAuth();
  const [sorting, setSorting] = useState<MRT_SortingState>([
    { id: "date_created", desc: true },
  ]);

  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: AppConfig.defaultPageSize,
  });

  const [columnFilters, setColumnFilters] = useState<
    MRT_TableState<CaseFile>["columnFilters"]
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
    columnFilters: MRT_TableState<CaseFile>["columnFilters"];
    externalFilters: Record<string, string[] | string>;
    globalFilter: string;
    sorting: MRT_SortingState;
    myFilesChecked: boolean;
  }>({
    columnFilters: [],
    externalFilters: {},
    globalFilter: "",
    sorting: [{ id: "date_created", desc: true }],
    myFilesChecked: true, // Default to true for first-time users
  });

  // Get cached filters store methods
  const { getFilters, getExternalFilters, getSorting } = cachedFiltersStore();
  const cachedColumnFilters = getFilters(caseFilesColumnFiltersCacheKey);
  const cachedExternalFilters = getExternalFilters(
    caseFilesColumnFiltersCacheKey
  );
  const cachedSorting = getSorting(caseFilesColumnFiltersCacheKey);

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
        const restoredSwitchState = Boolean(restoredExternalFilters.myFilesChecked);
        setMyFilesChecked(restoredSwitchState);
        
        // If switch is ON, ensure column filters are set up for UI display
        if (restoredSwitchState && currentUser?.profile?.preferred_username && staffList) {
          const currentStaff = staffList.find(
            (staff) => staff.auth_user_guid === currentUser.profile.preferred_username
          );
          if (currentStaff) {
            // Add primary_officer column filter for UI display
            const primaryOfficerColumnFilter = {
              id: "primary_officer",
              value: [currentStaff.id.toString()],
            };
            setColumnFilters(prev => {
              const filtered = prev.filter(filter => filter.id !== "primary_officer");
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
        if (derivedSwitchState && currentUser?.profile?.preferred_username && staffList) {
          const currentStaff = staffList.find(
            (staff) => staff.auth_user_guid === currentUser.profile.preferred_username
          );
          if (currentStaff) {
            // Add primary_officer column filter for UI display
            const primaryOfficerColumnFilter = {
              id: "primary_officer",
              value: [currentStaff.id.toString()],
            };
            setColumnFilters(prev => {
              const filtered = prev.filter(filter => filter.id !== "primary_officer");
              return [...filtered, primaryOfficerColumnFilter];
            });
          }
        }
      }
    } else {
      // No cached filters - apply default "My Files" filter for first-time users
      if (currentUser?.profile?.preferred_username && staffList) {
        const currentStaff = staffList.find(
          (staff) => staff.auth_user_guid === currentUser.profile.preferred_username
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
            {
              id: "status",
              value: ["Open"],
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
  }, [cachedColumnFilters, cachedExternalFilters, cachedSorting, staffList, currentUser?.profile?.preferred_username]);

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
          caseFilesColumnFiltersCacheKey,
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

  // Memoize external filters to prevent unnecessary recreations
  const memoizedExternalFilters = useMemo(
    () => externalFilters,
    [externalFilters]
  );

  // Use the extracted utility function
  const convertFiltersToQueryParams = useConvertFiltersToQueryParams(
    memoizedExternalFilters
  );

  const queryParams: CaseFileGridQueryParams = useMemo(() => {
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

  const { data, isLoading } = useCaseFilesData(queryParams);
  const caseFilesList = useMemo(() => data?.items ?? [], [data]);

  const handlePaginationChange = useCallback(
    (
      updater:
        | MRT_TableState<CaseFile>["pagination"]
        | ((
            old: MRT_TableState<CaseFile>["pagination"]
          ) => MRT_TableState<CaseFile>["pagination"])
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
        | MRT_TableState<CaseFile>["columnFilters"]
        | ((
            old: MRT_TableState<CaseFile>["columnFilters"]
          ) => MRT_TableState<CaseFile>["columnFilters"])
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
        | MRT_TableState<CaseFile>["globalFilter"]
        | ((
            old: MRT_TableState<CaseFile>["globalFilter"]
          ) => MRT_TableState<CaseFile>["globalFilter"])
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
      columnFilters?: MRT_TableState<CaseFile>["columnFilters"];
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
    [externalFilters, myFilesChecked, handleColumnFiltersChange]
  );

  // Use the extracted utility function for columns
  const columns = useCaseFileGridColumns({
    projectList: projects,
    initiationList: initiations,
    staffUserList: staffList,
  });

  // Create case file functionality
  const queryClient = useQueryClient();
  const { setOpen, setClose } = useDrawer();
  const showCreateCaseFileButton = useIsRolesAllowed([
    KC_USER_GROUPS.USER,
    KC_USER_GROUPS.SUPERUSER,
  ]);

  const handleOnSubmit = useCallback(
    (submitMsg: string) => {
      queryClient.invalidateQueries({ queryKey: ["case-files"] });
      setClose();
      notify.success(submitMsg);
    },
    [queryClient, setClose]
  );

  const handleOpenModal = useCallback(() => {
    setOpen({
      content: <CaseFileDrawer onSubmit={handleOnSubmit} />,
      width: DRAWER_WIDTHS.CASEFILE_DRAWER,
    });
  }, [setOpen, handleOnSubmit]);

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
      data={caseFilesList ?? []}
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
          {/* Title section with toggle and create button */}
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
              Case Files
            </Typography>
            <Box display="flex" alignItems="center" gap={2}>
              <ShowOnlyMyCaseFilesSwitch
                staffUsers={staffList ?? []}
                onFiltersChange={handleMyFilesSwitchChange}
                initialChecked={myFilesChecked}
              />
              {showCreateCaseFileButton && (
                <Button onClick={handleOpenModal} startIcon={<AddRounded />}>
                  Case File
                </Button>
              )}
            </Box>
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
              <CaseFileGridExport queryParams={queryParams} />
              <CaseFileGridPagination
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
