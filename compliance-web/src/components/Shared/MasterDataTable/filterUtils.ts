import type { MRT_ColumnFiltersState } from "material-react-table";

export const isFilterValueActive = (value: unknown): boolean => {
  if (value === undefined || value === null) return false;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "string") return value.trim() !== "";
  return true;
};

export const hasActiveFilters = (
  columnFilters: MRT_ColumnFiltersState,
  externalFilters: Record<string, unknown> = {},
): boolean =>
  columnFilters.some((filter) => isFilterValueActive(filter.value)) ||
  Object.values(externalFilters).some(isFilterValueActive);
