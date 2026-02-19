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
import { DRAWER_WIDTHS, STAFF_USER_POSITION } from "@/utils/constants";
import { AppConfig } from "@/utils/config";
import { Box, Button, CircularProgress, Typography } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
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
import { useTableHandlers } from "@/components/Shared/MasterDataTable/useTableHandlers";
import {
  useConvertFiltersToQueryParams,
  useCaseFileGridColumns,
} from "@/components/App/CaseFiles/CaseFileGrid/CaseFileGridUtils";
import CaseFileGridExport from "@/components/App/CaseFiles/CaseFileGrid/CaseFileGridExport";
import ShowOnlyMyCaseFilesSwitch from "@/components/App/CaseFiles/CaseFileGrid/ShowOnlyMyCaseFilesSwitch";
import { AddRounded } from "@mui/icons-material";
import Pagination from "@/components/Shared/Pagination";

export const Route = createFileRoute("/_authenticated/ce-database/case-files/")(
  {
    component: CaseFiles,
  }
);

const caseFilesColumnFiltersCacheKey = "case-files-column-filters";

export function CaseFiles() {
  const { data: projects } = useProjectsData();
  const { data: initiations } = useInitiationsData();
  const { data: staffList, isLoading: staffLoading } = useStaffUsersData({ isActive: true, otherPositions: false });
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
  const [isRestored, setIsRestored] = useState(false);

  // Ref to track if filters have been initialized
  const filtersInitialized = useRef(false);

  // Get cached filters store methods
  const { getFilters, getExternalFilters, getSorting } = cachedFiltersStore();
  const cachedColumnFilters = getFilters(caseFilesColumnFiltersCacheKey);
  const cachedExternalFilters = getExternalFilters(
    caseFilesColumnFiltersCacheKey
  );
  const cachedSorting = getSorting(caseFilesColumnFiltersCacheKey);

  const currentStaff = useMemo(() => {
    if (!currentUser?.profile?.preferred_username || !staffList) return null;
    return staffList.find(
      (staff) => staff.auth_user_guid === currentUser.profile.preferred_username
    );
  }, [currentUser?.profile?.preferred_username, staffList]);

  // Restore cached filters on component mount
  useEffect(() => {
    // Prevent re-initialization if already done
    if (filtersInitialized.current) return;

    // Wait for currentStaff to be available before initializing
    if (!currentStaff) return;

    let restoredFilters = false;

    // Restore column filters
    if (cachedColumnFilters.length > 0) {
      setColumnFilters(cachedColumnFilters);
      restoredFilters = true;
    }

    // Restore external filters
    if (cachedExternalFilters) {
      const restoredExternalFilters = cachedExternalFilters as Record<
        string,
        string[] | string
      >;
      setExternalFilters(restoredExternalFilters);

      // Restore global filter
      if (restoredExternalFilters.globalFilter) {
        setGlobalFilter(restoredExternalFilters.globalFilter as string);
      }

      // Restore "My Files" switch state
      if (restoredExternalFilters.myFilesChecked !== undefined) {
        const restoredSwitchState = Boolean(
          restoredExternalFilters.myFilesChecked
        );
        setMyFilesChecked(restoredSwitchState);

        // Set up column filters for UI display if switch is ON
        if (restoredSwitchState) {
          setColumnFilters((prev) => {
            const filtered = prev.filter((f) => f.id !== "primary_officer");
            return [
              ...filtered,
              { id: "primary_officer", value: [currentStaff.id.toString()] },
            ];
          });
        }
      } else {
        // Fallback: derive from primary_officer filter
        const primaryOfficerFilter =
          restoredExternalFilters.primary_officer_ids || [];
        const derivedSwitchState = primaryOfficerFilter.length > 0;
        setMyFilesChecked(derivedSwitchState);

        if (derivedSwitchState) {
          setColumnFilters((prev) => {
            const filtered = prev.filter((f) => f.id !== "primary_officer");
            return [
              ...filtered,
              { id: "primary_officer", value: [currentStaff.id.toString()] },
            ];
          });
        }
      }
      restoredFilters = true;
    }

    // Apply default filters for first-time users
    if (!restoredFilters) {
      const officerPositions = [
        STAFF_USER_POSITION.OFFICER,
        STAFF_USER_POSITION.SENIOR_OFFICER,
      ];
      const defaultChecked = Boolean(currentStaff.position_id && 
        officerPositions.includes(currentStaff.position_id));

      const defaultExternalFilters = {
        primary_officer_ids: [defaultChecked ? currentStaff.id.toString() : ""],
      };
      const defaultColumnFilters = [
        { id: "primary_officer", value: [defaultChecked ? currentStaff.id.toString() : ""] },
        { id: "status", value: ["Open"] },
      ];

      setExternalFilters(defaultExternalFilters);
      setColumnFilters(defaultColumnFilters);
      setMyFilesChecked(defaultChecked);
    }

    // Restore sorting
    if (cachedSorting && cachedSorting.length > 0 && cachedSorting[0]?.id) {
      setSorting(cachedSorting);
    }

    // Mark initialization complete
    setTimeout(() => {
      filtersInitialized.current = true;
      setIsRestored(true);
    }, 0);
  }, [
    cachedColumnFilters,
    cachedExternalFilters,
    cachedSorting,
    currentStaff,
  ]);

  // Cache after filters stabilize
  const cacheTimeoutRef = useRef<NodeJS.Timeout>();
  
  useEffect(() => {
    // Don't cache until filters are initialized
    if (!filtersInitialized.current) return;

    // Clear existing timeout
    if (cacheTimeoutRef.current) {
      clearTimeout(cacheTimeoutRef.current);
    }

    // Debounce cache updates by 300ms to avoid excessive writes
    cacheTimeoutRef.current = setTimeout(() => {
      cachedFiltersStore.getState().setFilters(
        caseFilesColumnFiltersCacheKey,
        columnFilters,
        {
          ...externalFilters,
          globalFilter,
          myFilesChecked,
        },
        sorting
      );
    }, 300);

    return () => {
      if (cacheTimeoutRef.current) {
        clearTimeout(cacheTimeoutRef.current);
      }
    };
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

  // Memoize query params with stable dependencies
  const queryParams: CaseFileGridQueryParams = useMemo(() => {
    const currentSort = sorting[0];
    const convertedFilters = convertFiltersToQueryParams(columnFilters);

    return {
      page_no: pagination.pageIndex + 1,
      page_size: pagination.pageSize,
      ...convertedFilters,
      ...(currentSort && {
        sort_by: currentSort.id,
        sort_order: currentSort.desc ? "desc" : "asc",
      }),
    };
  }, [
    pagination.pageIndex,
    pagination.pageSize,
    sorting,
    columnFilters,
    convertFiltersToQueryParams,
  ]);

  // Only fetch data when filters are initialized
  const { data, isLoading } = useCaseFilesData(
    filtersInitialized.current ? queryParams : undefined
  );
  
  const caseFilesList = useMemo(() => data?.items ?? [], [data?.items]);

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
            (filter) => filter.id === "primary_officer"
          );
          
          // If user removed the primary_officer_ids filter, re-add it
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
    [myFilesChecked, currentStaff]
  );

  // "My Files" switch handler
  const handleMyFilesSwitchChange = useCallback(
    (filters: {
      checked: boolean;
      externalFilters: Record<string, string[] | string>;
      columnFilters?: MRT_TableState<CaseFile>["columnFilters"];
    }) => {
      // State updates
      setMyFilesChecked(filters.checked);
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

  // Show loading only when actually loading data, not during initialization
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
      data={caseFilesList}
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
      enableSorting={true}
      enablePagination={false}
      hideFilterToggle={true}
      renderTopToolbarCustomActions={({
        table,
      }: {
        table: MRT_TableInstance<CaseFile>;
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
