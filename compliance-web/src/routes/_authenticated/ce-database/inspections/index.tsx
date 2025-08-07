import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import { useInspectionsData } from "@/hooks/useInspections";
import { useStaffUsersData } from "@/hooks/useStaff";
import { useProjectsData } from "@/hooks/useProjects";
import { useInitiationsData } from "@/hooks/useInspections";
import { Inspection, InspectionGridQueryParams } from "@/models/Inspection";
import { cachedFiltersStore } from "@/store/cachedFiltersStore";
import {
  APPROVAL_STATUS_TEXT,
  IRProgressEnumText,
  InspectionStatusEnum,
} from "@/utils/constants";
import { Box, CircularProgress, Typography } from "@mui/material";
import { createFileRoute } from "@tanstack/react-router";
import { BCDesignTokens } from "epic.theme";
import { MRT_TableState, MRT_SortingState } from "material-react-table";
import { useCallback, useEffect, useMemo, useState, useRef } from "react";
import { useAuth } from "react-oidc-context";
import InspectionsGridPagination from "@/components/App/Inspections/InspectionsGrid/InspectionsGridPagination";
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
  const { data: staffList, isLoading: staffLoading } = useStaffUsersData(true);
  const { isLoading: authLoading } = useAuth();
  const [showOnlyMyInspections, setShowOnlyMyInspections] = useState(false);
  const [sorting, setSorting] = useState<MRT_SortingState>([
    { id: "ir_number", desc: false },
  ]);

  const approvalStatusOptions = Object.entries(APPROVAL_STATUS_TEXT).map(
    ([id, name]) => ({
      id,
      name,
    })
  );

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
    showOnlyMyInspections: boolean;
    globalFilter: string;
    sorting: MRT_SortingState;
  }>({
    columnFilters: [],
    externalFilters: {},
    showOnlyMyInspections: false,
    globalFilter: "",
    sorting: [{ id: "ir_number", desc: false }],
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

      // Restore showOnlyMyInspections state if it was cached
      if (restoredExternalFilters.showOnlyMyInspections !== undefined) {
        const showOnlyMyInspectionsValue =
          restoredExternalFilters.showOnlyMyInspections;
        if (typeof showOnlyMyInspectionsValue === "boolean") {
          setShowOnlyMyInspections(showOnlyMyInspectionsValue);
        }
      }

      // Restore global filter if it was cached
      if (restoredExternalFilters.globalFilter) {
        setGlobalFilter(restoredExternalFilters.globalFilter as string);
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
        showOnlyMyInspections,
        globalFilter,
        sorting,
      };

      const hasChanged =
        JSON.stringify(currentFilters) !== JSON.stringify(prevFilters.current);

      if (hasChanged) {
        cachedFiltersStore.getState().setFilters(
          inspectionsColumnFiltersCacheKey,
          columnFilters,
          {
            ...externalFilters,
            showOnlyMyInspections,
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
    showOnlyMyInspections,
    globalFilter,
    sorting,
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

  const handlePaginationChange = useCallback(
    (
      updater:
        | MRT_TableState<Inspection>["pagination"]
        | ((
            old: MRT_TableState<Inspection>["pagination"]
          ) => MRT_TableState<Inspection>["pagination"])
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
        | MRT_TableState<Inspection>["columnFilters"]
        | ((
            old: MRT_TableState<Inspection>["columnFilters"]
          ) => MRT_TableState<Inspection>["columnFilters"])
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
        | MRT_TableState<Inspection>["globalFilter"]
        | ((
            old: MRT_TableState<Inspection>["globalFilter"]
          ) => MRT_TableState<Inspection>["globalFilter"])
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

  // Use the extracted utility function for columns
  const columns = useInspectionsGridColumns({
    projectList: projects,
    initiationList: initiations,
    irProgressList: irProgressOptions,
    approvalStatusList: approvalStatusOptions,
    reviewerList: staffList,
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
              Inspections
            </Typography>
            <ShowOnlyMyInspectionsSwitch
              initialChecked={showOnlyMyInspections}
              onFiltersChange={({
                checked,
                externalFilters,
                columnFilters,
              }) => {
                setShowOnlyMyInspections(checked);
                if (externalFilters) {
                  Object.entries(externalFilters).forEach(([key, value]) => {
                    setExternalFilters((prev) => ({
                      ...prev,
                      [key]: value,
                    }));
                  });
                }
                if (columnFilters) {
                  handleColumnFiltersChange(columnFilters);
                }
              }}
              disabled={isLoading}
              onColumnFiltersChange={handleColumnFiltersChange}
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
