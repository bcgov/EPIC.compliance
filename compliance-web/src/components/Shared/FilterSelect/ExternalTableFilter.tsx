import { ComponentType, FC, useCallback, useMemo, memo } from "react";
import FilterSelect from "./FilterSelect";
import { ExternalTableFilterProps } from "./type";

interface ExternalTableFilterPropsWithValue extends ExternalTableFilterProps {
  currentValue?: string[] | string;
}

const makeExternalTableFilter = <SelectProps extends object>(
  Component: ComponentType<SelectProps>
): FC<ExternalTableFilterPropsWithValue> =>
  memo(
    ({
      filterId,
      filterOptions,
      onFilterChange,
      isMulti = true,
      currentValue,
      ...props
    }: ExternalTableFilterPropsWithValue) => {
      const filterAppliedCallback = useCallback(
        (selectedOptions: string[] | string) => {
          onFilterChange(filterId, selectedOptions);
        },
        [filterId, onFilterChange]
      );

      const filterClearedCallback = useCallback(
        (value: [] | string) => {
          onFilterChange(filterId, value);
        },
        [filterId, onFilterChange]
      );

      const toOptionType = useCallback(
        (option: string | { text: string; value: unknown }) => {
          if (typeof option === "object") {
            return { label: option.text, value: option.value };
          }
          return { label: option, value: option };
        },
        []
      );

      const options = useMemo(() => {
        const filterOptionsList = filterOptions.map(
          (
            option:
              | string
              | {
                  text: string;
                  value: unknown;
                }
          ) => toOptionType(option)
        );
        return filterOptionsList.sort((a, b) => a.label.localeCompare(b.label));
      }, [filterOptions, toOptionType]);

          // Create dynamic placeholder with count
    const dynamicPlaceholder = useMemo(() => {
      const basePlaceholder = props.placeholder || "Filter";
      if (
        !currentValue ||
        (Array.isArray(currentValue) && currentValue.length === 0) ||
        (!Array.isArray(currentValue) && currentValue === "")
      ) {
        return basePlaceholder;
      }
      
      const count = Array.isArray(currentValue) ? currentValue.length : 1;
      return `${basePlaceholder} (${count})`;
    }, [props.placeholder, currentValue]);

    // Convert current values to option objects for the Select component
    const currentValueAsOptions = useMemo(() => {
      if (!currentValue) return isMulti ? [] : "";
      
      if (Array.isArray(currentValue)) {
        return currentValue
          .map(value => options.find(option => option.value === value))
          .filter(Boolean);
      } else {
        return options.find(option => option.value === currentValue) || "";
      }
    }, [currentValue, options, isMulti]);

    return (
      <Component
        {...(props as SelectProps)}
        options={options}
        filterAppliedCallback={filterAppliedCallback}
        filterClearedCallback={filterClearedCallback}
        defaultValue={isMulti ? [] : ""}
        isMulti={isMulti}
        placeholder={dynamicPlaceholder}
        value={currentValueAsOptions}
      />
    );
    }
  );

const ExternalTableFilter = makeExternalTableFilter(FilterSelect);
ExternalTableFilter.displayName = "ExternalTableFilter";
export default ExternalTableFilter;
