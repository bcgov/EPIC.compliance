import { useEffect, useState } from "react";
import {
  MaterialReactTable,
  MRT_ColumnDef,
  MRT_RowData,
  MRT_TableInstance,
  MRT_TableOptions,
  useMaterialReactTable,
} from "material-react-table";
import {
  Box,
  Button,
  Container,
  IconButton,
  Tooltip,
  Typography,
} from "@mui/material";
import { FiltersCache } from "./FiltersCache";
import { exportToCsv } from "./utils";
import { BCDesignTokens } from "epic.theme";
import {
  AddRounded,
  DownloadRounded,
  SearchRounded,
} from "@mui/icons-material";

const NoDataComponent = ({ ...props }) => {
  const { table } = props;
  return (
    <Container
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "400px",
      }}
    >
      <Box
        sx={{
          display: "flex",
          flexDirection: "column",
          gap: "2rem",
          alignItems: "center",
        }}
      >
        <SearchRounded sx={{ fontSize: "2rem" }} />
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
            alignItems: "center",
          }}
        >
          <Typography variant="h2" color="initial">
            No results found
          </Typography>
          {table.options.data.length > 0 && (
            <Typography variant="h4">
              Adjust your parameters and try again
            </Typography>
          )}
        </Box>
      </Box>
    </Container>
  );
};

interface MRT_EAO_TitleToolbarProps {
  tableTitle: string;
  tableAddRecordButtonText?: string;
  tableAddRecordButtonVisibility?: boolean;
  tableAddRecordFunction?: () => void;
}

export interface MaterialReactTableProps<TData extends MRT_RowData>
  extends MRT_TableOptions<TData> {
  columns: MRT_ColumnDef<TData>[];
  data: TData[];
  setTableInstance?: (instance: MRT_TableInstance<TData> | undefined) => void;
  onCacheFilters?: (columnFilters: unknown) => void;
  enableExport?: boolean;
  tableName?: string;
  titleToolbarProps?: MRT_EAO_TitleToolbarProps;
  isStackedTables?: boolean;
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
  ...rest
}: MaterialReactTableProps<TData>) => {
  const { initialState, state, icons, ...otherProps } = rest;
  const [otherPropsData, setOtherPropsData] = useState(otherProps);

  useEffect(() => {
    setOtherPropsData(otherProps);
  }, [columns, data, otherProps]);

  const checkBoxStyle = {
    width: "2.75rem !important",
    height: "2rem",
    padding: "8px !important",
    borderRadius: "4px",
  };

  const table = useMaterialReactTable({
    columns: columns,
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
    enablePagination: false,
    positionActionsColumn: "last",
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
      sx: { p: 0, m: "-0.5rem" },
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
      sx: { tableLayout: "fixed" },
      ...rest.muiTableProps,
    },
    muiTableBodyCellProps: () => ({
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
    muiTableContainerProps: () => ({
      sx: {
        maxHeight: "100%",
        marginTop: "1.5rem",
      },
    }),
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
    renderEmptyRowsFallback: ({ table }) => <NoDataComponent table={table} />,
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
                  alignItems: "center",
                }}
              >
                <Typography
                  variant="h5"
                  sx={{ color: BCDesignTokens.typographyColorLink }}
                >
                  {titleToolbarProps?.tableTitle}
                </Typography>
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
    icons: {
      FilterAltIcon: () => null,
      CloseIcon: () => null,
      ...icons,
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
