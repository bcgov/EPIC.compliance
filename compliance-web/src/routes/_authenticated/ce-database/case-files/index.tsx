import CaseFileDrawer from "@/components/App/CaseFiles/CaseFileDrawer";
import CustomSwitch from "@/components/Shared/Controlled/CustomSwitch";
import { MasterTableColumnFilter } from "@/components/Shared/FilterSelect/type";
import MasterDataTable from "@/components/Shared/MasterDataTable/MasterDataTable";
import PageLink from "@/components/Shared/PageLink";
import { KC_USER_GROUPS, useIsRolesAllowed } from "@/hooks/useAuthorization";
import { useCaseFilesData } from "@/hooks/useCaseFiles";
import { CaseFile } from "@/models/CaseFile";
import { useDrawer } from "@/store/drawerStore";
import { notify } from "@/store/snackbarStore";
import { cachedFiltersStore } from "@/store/cachedFiltersStore";
import { DRAWER_WIDTHS } from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { Chip, FormControlLabel, Typography } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { MRT_ColumnDef, MRT_TableInstance } from "material-react-table";
import { useMemo, useCallback, useState, useEffect } from "react";
import { useAuth } from "react-oidc-context";


export const Route = createFileRoute("/_authenticated/ce-database/case-files/")(
  {
    component: CaseFiles,
  }
);

const caseFilesColumnFiltersCacheKey = "case-files-column-filters";

export function CaseFiles() {
  const queryClient = useQueryClient();
  const { setOpen, setClose } = useDrawer();
  const { data: caseFilesList, isLoading } = useCaseFilesData();
  const { user: currentUser, isLoading: authLoading } = useAuth();
  const [showOnlyMyCaseFiles, setShowOnlyMyCaseFiles] = useState(false);
  const [tableInstance, setTableInstance] = useState<
    MRT_TableInstance<CaseFile> | undefined
  >();
  const showCreateCaseFileButton = useIsRolesAllowed([
    KC_USER_GROUPS.USER,
    KC_USER_GROUPS.SUPERUSER,
  ]);
  const { getFilters, setFilters, getExternalFilters } = cachedFiltersStore();
  const columnFilters = getFilters(caseFilesColumnFiltersCacheKey);
  const cachedExternalFilters = getExternalFilters(caseFilesColumnFiltersCacheKey);

  // Check if current user has primary case files
  const isCurrentUserHasPrimary = useMemo(() => {
    return caseFilesList?.some(
      (caseFile) =>
        caseFile.primary_officer?.auth_user_guid ===
        currentUser?.profile?.preferred_username
    );
  }, [caseFilesList, currentUser?.profile?.preferred_username]);

  // Helper function to apply filters based on user role
  const applyUserSpecificFilters = useCallback(
    (table: MRT_TableInstance<CaseFile>) => {
      if (isCurrentUserHasPrimary) {
        const currentFilters = table.getState().columnFilters;
        const userFilter = {
          id: "primary_officer",
          value: [currentUser?.profile?.name],
        };
        const statusFilter = {
          id: "case_file_status",
          value: ["Open"],
        };
        
        // Check if user filter already exists
        const existingUserFilterIndex = currentFilters.findIndex(
          filter => filter.id === "primary_officer"
        );
        
        // Check if status filter already exists
        const existingStatusFilterIndex = currentFilters.findIndex(
          filter => filter.id === "case_file_status"
        );
        
        const newFilters = [...currentFilters];
        
        if (existingUserFilterIndex >= 0) {
          // Update existing user filter
          newFilters[existingUserFilterIndex] = userFilter;
        } else {
          // Add user filter to existing filters
          newFilters.push(userFilter);
        }
        
        if (existingStatusFilterIndex >= 0) {
          // Update existing status filter
          newFilters[existingStatusFilterIndex] = statusFilter;
        } else {
          // Add status filter to existing filters
          newFilters.push(statusFilter);
        }
        
        table.setColumnFilters(newFilters);
      }
    },
    [isCurrentUserHasPrimary, currentUser?.profile?.name]
  );

  const createUniqueFilterList = useCallback(
    (key: keyof CaseFile, subKey?: string): string[] => {
      return [
        ...new Set(
          caseFilesList?.map((item) => {
            const value = item[key];
            if (typeof value === "object" && value !== null) {
              if (subKey && subKey in value) {
                return (value as unknown as Record<string, unknown>)[
                  subKey
                ] as string;
              }
              return "";
            }
            return typeof value === "string" ? value : "";
          })
        ),
      ].filter(Boolean) as string[];
    },
    [caseFilesList]
  );

  const projectList = useMemo(
    () => createUniqueFilterList("project", "name"),
    [createUniqueFilterList]
  );

  const initiationList = useMemo(
    () => createUniqueFilterList("initiation", "name"),
    [createUniqueFilterList]
  );

  const statusList = useMemo(
    () => createUniqueFilterList("case_file_status"),
    [createUniqueFilterList]
  );

  const staffUserList = useMemo(
    () => createUniqueFilterList("primary_officer", "name"),
    [createUniqueFilterList]
  );

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

  const columns = useMemo<MRT_ColumnDef<CaseFile>[]>(
    () => [
      {
        accessorKey: "case_file_number",
        header: "Case File #",
        filterFn: "contains",
        Cell: ({ row }) => {
          return (
            <PageLink
              to="/ce-database/case-files/$caseFileNumber"
              params={{
                caseFileNumber: row.original.case_file_number,
              }}
            />
          );
        },
      },
      {
        accessorKey: "project.name",
        header: "Project",
        filterVariant: "multi-select",
        filterSelectOptions: projectList,
      },
      {
        accessorKey: "initiation.name",
        header: "Initiation",
        filterVariant: "multi-select",
        filterSelectOptions: initiationList,
      },
      {
        accessorFn: (row) => dateUtils.formatDate(row.date_created),
        id: "date_created",
        header: "Date Created",
        filterFn: "contains",
      },
      {
        accessorKey: "case_file_status",
        header: "Status",
        Cell: ({ row }) => {
          return row.original.case_file_status ? (
            <Chip
              label={row.original.case_file_status}
              color={
                row.original.case_file_status?.toLowerCase() === "open"
                  ? "success"
                  : "error"
              }
              variant="outlined"
              size="small"
            />
          ) : (
            <></>
          );
        },
        filterVariant: "multi-select",
        filterSelectOptions: statusList,
      },
      {
        accessorFn: (row) => row.primary_officer?.name,
        id: "primary_officer",
        header: "Primary",
        filterVariant: "multi-select",
        filterSelectOptions: staffUserList,
      },
    ],
    [initiationList, projectList, staffUserList, statusList]
  );

  // Initialize external filter state from cache or user role
  useEffect(() => {
    if (cachedExternalFilters?.showOnlyMyCaseFiles !== undefined) {
      // Restore from cache
      setShowOnlyMyCaseFiles(cachedExternalFilters.showOnlyMyCaseFiles as boolean);
    } else if (isCurrentUserHasPrimary) {
      // Set based on user role if no cache
      setShowOnlyMyCaseFiles(true);
    } else {
      setShowOnlyMyCaseFiles(false);
    }
  }, [cachedExternalFilters, isCurrentUserHasPrimary]);

  // Apply filters when table instance is available and state changes
  useEffect(() => {
    if (tableInstance) {
      if (showOnlyMyCaseFiles && isCurrentUserHasPrimary) {
        // When external filter is ON, apply user-specific filter
        applyUserSpecificFilters(tableInstance);
      }
      // When external filter is OFF, do nothing - let cached column filters remain
    }
  }, [
    tableInstance,
    showOnlyMyCaseFiles,
    isCurrentUserHasPrimary,
    applyUserSpecificFilters,
  ]);

  const renderExternalFilter = useCallback(
    ({ table }: { table: MRT_TableInstance<CaseFile> }) => {
      return (
        <FormControlLabel
          control={
            <CustomSwitch
              checked={showOnlyMyCaseFiles}
              onChange={(e) => {
                setShowOnlyMyCaseFiles(e.target.checked);
                if (e.target.checked) {
                  // When turning ON, apply user-specific filter
                  applyUserSpecificFilters(table);
                } else {
                  // When turning OFF, remove both user-specific and status filters
                  const currentFilters = table.getState().columnFilters;
                  const filteredFilters = currentFilters.filter(
                    filter => filter.id !== "primary_officer" && filter.id !== "case_file_status"
                  );
                  table.setColumnFilters(filteredFilters);
                }
              }}
              size="small"
            />
          }
          label={
            <Typography variant="body1" mr={1}>
              <strong>{currentUser?.profile?.given_name}</strong>'s Files
            </Typography>
          }
          labelPlacement="start"
        />
      );
    },
    [
      showOnlyMyCaseFiles,
      currentUser,
      applyUserSpecificFilters,
    ]
  );

  const handleCacheFilters = (filters?: MasterTableColumnFilter[]) => {
    if (!filters) {
      return;
    }
    // Cache both column filters and external filter state
    setFilters(
      caseFilesColumnFiltersCacheKey, 
      filters, 
      { showOnlyMyCaseFiles }
    );
  };

  return (
    <>
      <MasterDataTable
        columns={columns}
        data={caseFilesList ?? []}
        setTableInstance={setTableInstance}
        initialState={{
          sorting: [
            {
              id: "case_file_number",
              desc: true,
            },
          ],
          columnFilters: columnFilters,
        }}
        state={{
          isLoading: isLoading || authLoading,
          showGlobalFilter: true,
        }}
        titleToolbarProps={{
          tableTitle: "Case Files",
          tableAddRecordButtonText: "Case File",
          tableAddRecordFunction: handleOpenModal,
          tableAddRecordButtonVisibility: showCreateCaseFileButton,
        }}
        renderExternalFilter={
          isCurrentUserHasPrimary ? renderExternalFilter : undefined
        }
        onCacheFilters={handleCacheFilters}
      />
    </>
  );
}
