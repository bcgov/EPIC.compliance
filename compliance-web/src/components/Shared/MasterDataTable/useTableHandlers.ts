import { useCallback } from "react";
import { MRT_TableState, MRT_SortingState, MRT_RowData } from "material-react-table";

export function useTableHandlers<TData extends MRT_RowData>({
  sorting,
  columnFilters,
  globalFilter,
  setSorting,
  setColumnFilters,
  setGlobalFilter,
  setPagination,
}: {
  sorting: MRT_SortingState;
  columnFilters: MRT_TableState<TData>["columnFilters"];
  globalFilter: string;
  setSorting: (updater: MRT_SortingState | ((old: MRT_SortingState) => MRT_SortingState)) => void;
  setColumnFilters: (updater: MRT_TableState<TData>["columnFilters"] | ((old: MRT_TableState<TData>["columnFilters"]) => MRT_TableState<TData>["columnFilters"])) => void;
  setGlobalFilter: (updater: string | ((old: string) => string)) => void;
  setPagination: (updater: MRT_TableState<TData>["pagination"] | ((old: MRT_TableState<TData>["pagination"]) => MRT_TableState<TData>["pagination"])) => void;
}) {
  const handlePaginationChange = useCallback(
    (
      updater:
        | MRT_TableState<TData>["pagination"]
        | ((
          old: MRT_TableState<TData>["pagination"]
        ) => MRT_TableState<TData>["pagination"])
    ) => {
      setPagination(updater);
    },
    [setPagination]
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
    [sorting, setSorting, setPagination]
  );

  const handleColumnFiltersChange = useCallback(
    (
      updater:
        | MRT_TableState<TData>["columnFilters"]
        | ((
          old: MRT_TableState<TData>["columnFilters"]
        ) => MRT_TableState<TData>["columnFilters"])
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
    [columnFilters, setColumnFilters, setPagination]
  );

  const handleGlobalFilterChange = useCallback(
    (
      updater:
        | MRT_TableState<TData>["globalFilter"]
        | ((
          old: MRT_TableState<TData>["globalFilter"]
        ) => MRT_TableState<TData>["globalFilter"])
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
    [globalFilter, setGlobalFilter, setPagination]
  );

  return {
    handlePaginationChange,
    handleSortingChange,
    handleColumnFiltersChange,
    handleGlobalFilterChange,
  };
}
