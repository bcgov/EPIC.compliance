import { useEffect, useCallback, useMemo } from "react";
import {
  MaterialReactTable,
  MRT_ColumnDef,
  MRT_RowData,
  MRT_TableInstance,
  MRT_TableOptions,
  useMaterialReactTable,
  MRT_Column,
  MRT_Header,
  MRT_TableState,
  MRT_SortingState,
} from "material-react-table";
import { Box, Button, IconButton, Tooltip, Typography } from "@mui/material";
import { FiltersCache } from "./FiltersCache";
import { exportToCsv } from "./utils";
import { BCDesignTokens } from "epic.theme";
import { AddRounded, DownloadRounded } from "@mui/icons-material";
import DataTableNoData from "./DataTableNoData";
import TableFilter from "@/components/Shared/FilterSelect/TableFilter";
import DateFilter from "@/components/Shared/FilterSelect/DateFilter";
import { MasterTableColumnFilter } from "@/components/Shared/FilterSelect/type";

interface MRT_EAO_TitleToolbarProps {
  tableTitle: string;
  tableAddRecordButtonText?: string;
  tableAddRecordButtonVisibility?: boolean;
  tableAddRecordFunction?: () => void;
}

// interfaces for remote data
interface RemoteDataConfig<TData extends MRT_RowData> {
  enableRemoteData: boolean;
  rowCount?: number;
  manualPagination?: boolean;
  manualSorting?: boolean;
  manualFiltering?: boolean;
  onPaginationChange?: (
    updater:
      | MRT_TableState<TData>["pagination"]
      | ((
          old: MRT_TableState<TData>["pagination"]
        ) => MRT_TableState<TData>["pagination"])
  ) => void;
  onSortingChange?: (
    updater: MRT_SortingState | ((old: MRT_SortingState) => MRT_SortingState)
  ) => void;
  onColumnFiltersChange?: (
    updater:
      | MRT_TableState<TData>["columnFilters"]
      | ((
          old: MRT_TableState<TData>["columnFilters"]
        ) => MRT_TableState<TData>["columnFilters"])
  ) => void;
  onGlobalFilterChange?: (
    updater:
      | MRT_TableState<TData>["globalFilter"]
      | ((
          old: MRT_TableState<TData>["globalFilter"]
        ) => MRT_TableState<TData>["globalFilter"])
  ) => void;
}

export interface MaterialReactTableProps<TData extends MRT_RowData>
  extends MRT_TableOptions<TData> {
  columns: MRT_ColumnDef<TData>[];
  data: TData[];
  setTableInstance?: (instance: MRT_TableInstance<TData> | undefined) => void;
  onCacheFilters?: (columnFilters: MasterTableColumnFilter[]) => void;
  enableExport?: boolean;
  tableName?: string;
  titleToolbarProps?: MRT_EAO_TitleToolbarProps;
  isStackedTables?: boolean;
  renderExternalFilter?: (props: {
    table: MRT_TableInstance<TData>;
  }) => React.ReactNode;
  // Add remote data configuration
  remoteDataConfig?: RemoteDataConfig<TData>;
  hideFilterToggle?: boolean;
}

const MasterDataTable = <TData extends MRT_RowData>({
  columns,
  data,
  setTableInstance,
  onCacheFilters,
  tableName,
  titleToolbarProps,
  enableExport,
  renderTopToolbarCustomActions,
  isStackedTables,
  renderExternalFilter,
  remoteDataConfig,
  hideFilterToggle,
  ...rest
}: MaterialReactTableProps<TData>) => {
  const { initialState, state, ...otherProps } = rest;

  // Use useMemo instead of useState and useEffect to prevent unnecessary re-renders
  const otherPropsData = useMemo(() => otherProps, [otherProps]);

  const checkBoxStyle = useMemo(
    () => ({
      width: "2.75rem !important",
      height: "2rem",
      padding: "8px !important",
      borderRadius: "4px",
    }),
    []
  );

  // Memoize the Filter component to prevent recreation on every render
  const createFilterComponent = useCallback(
    (props: { column: MRT_Column<TData>; header: MRT_Header<TData> }) => (
      <TableFilter
        isMulti
        header={props.header}
        column={props.column}
        variant="inline"
        name={`${props.column.id}Filter`}
        placeholder={"Filter"}
      />
    ),
    []
  );

  // Memoize the Date Filter component to prevent recreation on every render
  const createDateFilterComponent = useCallback(
    (props: { column: MRT_Column<TData>; header: MRT_Header<TData> }) => (
      <DateFilter
        header={props.header as MRT_Header<MRT_RowData>}
        column={props.column as MRT_Column<MRT_RowData>}
        placeholder={props.column.columnDef.header}
      />
    ),
    []
  );

  // Memoize the columns mapping to prevent recreation on every render
  const mappedColumns = useMemo(
    () =>
      columns.map((column) => ({
        ...column,
        ...(column.filterSelectOptions &&
          column.filterVariant === "multi-select" && {
            Filter: createFilterComponent,
          }),
        ...(column.filterVariant === "date" && {
          Filter: createDateFilterComponent,
        }),
      })),
    [columns, createFilterComponent, createDateFilterComponent]
  );

  // Memoize the table body cell props to prevent recreation on every render
  const muiTableBodyCellProps = useCallback(
    () => ({
      disabled: true,
      sx: {
        padding: "0",
        paddingLeft: "1rem",
        height: "3rem",
        "& .MuiCheckbox-root": {
          ...checkBoxStyle,
          "&.Mui-disabled": {
            svg: {
              fill: BCDesignTokens.surfaceColorFormsDisabled,
            },
          },
        },
      },
    }),
    [checkBoxStyle]
  );

  // Memoize the table container props to prevent recreation on every render
  const muiTableContainerProps = useCallback(
    () => ({
      sx: {
        maxHeight: "100%",
        marginTop: "1.5rem",
      },
    }),
    []
  );

  const table = useMaterialReactTable({
    columns: mappedColumns,
    data: data,
    globalFilterFn: "contains",
    enableHiding: false,
    layoutMode: "grid",
    enableGlobalFilter: false,
    enableColumnResizing: true,
    enableStickyHeader: true,
    enableDensityToggle: false,
    enableColumnFilters: true,
    enableFullScreenToggle: false,
    enableSorting: true,
    enableFilters: true,
    enableColumnActions: false,
    enablePinning: true,
    // Enable pagination for remote data
    enablePagination: remoteDataConfig?.enableRemoteData ?? false,
    positionActionsColumn: "last",

    // Remote data configuration
    ...(remoteDataConfig?.enableRemoteData && {
      manualPagination: remoteDataConfig.manualPagination ?? true,
      manualSorting: remoteDataConfig.manualSorting ?? true,
      manualFiltering: remoteDataConfig.manualFiltering ?? true,
      rowCount: remoteDataConfig.rowCount,
      onPaginationChange: remoteDataConfig.onPaginationChange,
      onSortingChange: remoteDataConfig.onSortingChange,
      onColumnFiltersChange: remoteDataConfig.onColumnFiltersChange,
      onGlobalFilterChange: remoteDataConfig.onGlobalFilterChange,
    }),

    muiTableHeadProps: {
      sx: {
        "& .MuiTableRow-root": {
          boxShadow: "none",
        },
      },
    },
    muiTableHeadCellProps: {
      sx: {
        backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
        padding: "1rem 0.5rem 0.5rem 1rem !important",
        "& .Mui-TableHeadCell-Content-Labels": {
          fontSize: BCDesignTokens.typographyFontSizeBody,
          fontWeight: BCDesignTokens.typographyFontWeightsBold,
          color: BCDesignTokens.themeGray90,
          paddingBottom: BCDesignTokens.layoutPaddingSmall,
        },
        "& .MuiTextField-root": {
          minWidth: "0",
        },
        "& .MuiCheckbox-root": checkBoxStyle,
      },
    },
    muiTopToolbarProps: {
      sx: {
        p: 0,
        m: "-0.5rem",
        "& .MuiIconButton-root[aria-label='Show/Hide filters']": {
          display: hideFilterToggle ? "none" : "block",
        },
      },
    },
    muiBottomToolbarProps: {
      sx: {
        boxShadow: "none",
        ...(isStackedTables && {
          display: "none",
        }),
      },
    },
    muiTablePaperProps: {
      sx: {
        boxShadow: "none",
        pb: "4rem",
        ...(isStackedTables && {
          pb: "0",
        }),
      },
    },
    muiTableProps: {
      sx: { tableLayout: "fixed", pb: "4rem" },
      ...rest.muiTableProps,
    },
    muiTableBodyCellProps,
    muiFilterTextFieldProps: ({ column }) => ({
      placeholder: column.columnDef.header,
      variant: "outlined",
      size: "small",
      sx: {
        backgroundColor: BCDesignTokens.surfaceColorBackgroundWhite,
        mb: 0,
        "& .MuiInputAdornment-root": {
          display: "none",
        },
        "& .MuiSelect-icon": {
          mr: "0px !important",
        },
      },
    }),
    muiTableContainerProps,
    muiTableBodyProps: {
      sx: {
        "& tr:hover td": {
          backgroundColor: BCDesignTokens.surfaceColorBackgroundLightBlue,
        },
      },
    },
    muiTableBodyRowProps: {
      hover: true,
      sx: {
        "&.Mui-selected": {
          backgroundColor: BCDesignTokens.surfaceColorBackgroundDarkBlue,
        },
        "&.MuiTableRow-hover:hover": {
          backgroundColor: BCDesignTokens.surfaceColorBackgroundLightBlue,
        },
      },
    },
    sortingFns: {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      sortFn: (rowA: any, rowB: any, columnId: string) => {
        return rowA
          ?.getValue(columnId)
          ?.localeCompare(rowB?.getValue(columnId), "en", {
            numeric: true,
            ignorePunctuation: false,
            sensitivity: "base",
          });
      },
    },
    renderEmptyRowsFallback: ({ table }) => <DataTableNoData table={table} />,
    renderTopToolbarCustomActions: ({ table }) => {
      return (
        <>
          {titleToolbarProps &&
            !renderTopToolbarCustomActions && ( // generic title toolbar of all EAO tables
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
                  {titleToolbarProps?.tableTitle}
                </Typography>
                <Box display="flex" alignItems="center" gap={2}>
                  {renderExternalFilter && renderExternalFilter({ table })}
                  {titleToolbarProps?.tableAddRecordButtonVisibility && (
                    <Button
                      id="addActionButton"
                      startIcon={<AddRounded />}
                      onClick={titleToolbarProps?.tableAddRecordFunction}
                    >
                      {titleToolbarProps?.tableAddRecordButtonText}
                    </Button>
                  )}
                </Box>
              </Box>
            )}
          {renderTopToolbarCustomActions && // custom title toolbar
            renderTopToolbarCustomActions({ table })}
          {enableExport && ( //common for both toolbars
            <Tooltip title="Export to csv">
              <IconButton
                aria-label="download"
                onClick={() =>
                  exportToCsv({
                    table,
                    downloadDate: new Date().toISOString(),
                    filenamePrefix: tableName || "exported-data",
                  })
                }
              >
                <DownloadRounded />
              </IconButton>
            </Tooltip>
          )}
        </>
      );
    }, // Provide an empty function as the initializer
    initialState: {
      showColumnFilters: true,
      density: "compact",
      columnPinning: { right: ["mrt-row-actions"] },
      ...initialState,
    },
    state: {
      showGlobalFilter: true,
      columnPinning: { right: ["mrt-row-actions"] },
      ...state,
    },
    filterFns: {
      multiSelectFilter: (row, id, filterValue) => {
        if (filterValue.length === 0) return true;
        return filterValue.includes(row.getValue(id));
      },
    },
    ...otherPropsData,
  });

  useEffect(() => {
    if (table && setTableInstance) {
      setTableInstance(table);
    }
  }, [setTableInstance, table]);

  return (
    <>
      <MaterialReactTable table={table} />
      {onCacheFilters && (
        <FiltersCache onCacheFilters={onCacheFilters} table={table} />
      )}
    </>
  );
};

export default MasterDataTable;
