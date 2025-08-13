import { ComponentType, FC, useCallback, useMemo, memo } from "react";

import FilterSelect from "./FilterSelect";
import { TableFilterProps } from "./type";

const makeTableFilter =
  <SelectProps extends object>(
    Component: ComponentType<SelectProps>
  ): FC<TableFilterProps> =>
  memo(({ header, column, ...props }: TableFilterProps) => {
    const filterAppliedCallback = useCallback(
      (selectedOptions: string[] | string) => {
        header.column.setFilterValue(selectedOptions);
      },
      [header.column]
    );

    const filterClearedCallback = useCallback(
      (value: [] | string) => {
        header.column.setFilterValue(value);
      },
      [header.column]
    );

    const toOptionType = useCallback((
      option: string | { text: string; value: unknown }
    ) => {
      if (typeof option === "object") {
        return { label: option.text, value: option.value };
      }
      return { label: option, value: option };
    }, []);

    const options = useMemo(() => {
      let filterOptions = column.columnDef.filterSelectOptions;
      filterOptions = filterOptions.map(
        (
          option:
            | string
            | {
                text: string;
                value: unknown;
              }
        ) => toOptionType(option)
      );
      return filterOptions.sort((a: { label: string; }, b: { label: string; }) => a.label.localeCompare(b.label));
    }, [column.columnDef.filterSelectOptions, toOptionType]);

    const handleValues = useCallback((value: string | string[]) => {
      if (!value) return [];
      if (Array.isArray(value)) {
        return value.map((val) => {
          return toOptionType(val);
        });
      }
      return toOptionType(value);
    }, [toOptionType]);

    return (
      <Component
        {...(props as SelectProps)}
        options={options}
        filterAppliedCallback={filterAppliedCallback}
        filterClearedCallback={filterClearedCallback}
        value={handleValues(column.getFilterValue())}
      />
    );
  });

const TableFilter = makeTableFilter(FilterSelect);
TableFilter.displayName = 'TableFilter';
export default TableFilter;
