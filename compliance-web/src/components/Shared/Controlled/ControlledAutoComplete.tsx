import {
  ExpandMore,
  CheckBox,
  CheckBoxOutlineBlank,
  Close,
} from "@mui/icons-material";
import {
  Autocomplete,
  TextField,
  Checkbox,
  AutocompleteProps,
  Chip,
  Box,
  Popper,
  PopperProps,
} from "@mui/material";
import { useEffect, useMemo } from "react";
import { Controller, useFormContext } from "react-hook-form";
import { VARIANT_COLORS } from "@/utils/constants";

interface FormAutocompleteProps<T> extends Partial<
  AutocompleteProps<T, true | false, false, false>
> {
  name: string;
  label: string;
  options: T[];
  getOptionLabel: (option: T) => string;
  isOptionEqualToValue: (option: T, value: T) => boolean;
  multiple?: boolean;
  placeholder?: string;
  onDeleteOption?: (option: T) => void;
  isSortOptions?: boolean;
  isRequired?: boolean;
  renderOptionBadge?: (
    option: T,
  ) => { label: string; color: VARIANT_COLORS } | null;
  showSelectAllOption?: boolean;
  showAllSelectedText?: boolean;
  defaultAllSelected?: boolean;
}

const ControlledAutoComplete = <T,>({
  name,
  label,
  options,
  getOptionLabel,
  isOptionEqualToValue,
  multiple,
  placeholder = "Select an option...",
  onDeleteOption,
  isSortOptions = false,
  isRequired = false,
  renderOptionBadge,
  showSelectAllOption = false,
  showAllSelectedText = false,
  defaultAllSelected = false,
  ...props
}: FormAutocompleteProps<T>) => {
  const {
    control,
    formState: { errors, defaultValues },
    setValue,
  } = useFormContext();

  const sortedOptions = useMemo(() => {
    if (isSortOptions) {
      return options.sort((a, b) =>
        getOptionLabel(a).localeCompare(getOptionLabel(b)),
      );
    }
    return options;
  }, [isSortOptions, options, getOptionLabel]);

  const CustomPopper = (props: PopperProps) => (
    <Popper
      {...props}
      placement="bottom-start"
      modifiers={[{ name: "flip", enabled: false }]}
    />
  );

  const selectAllOption = useMemo(
    () => ({
      name: "Select All",
    }),
    [],
  );

  useEffect(() => {
    if (defaultAllSelected && multiple) {
      const options = showSelectAllOption
        ? [selectAllOption as T, ...sortedOptions]
        : sortedOptions;
      setValue(name, options);
    }
  }, [
    defaultAllSelected,
    multiple,
    name,
    setValue,
    showSelectAllOption,
    selectAllOption,
    sortedOptions,
  ]);

  return (
    <Controller
      name={name}
      control={control}
      defaultValue={defaultValues?.[name] || (multiple ? [] : undefined)}
      render={({ field }) => (
        <Autocomplete
          {...field}
          {...props}
          id={name}
          PopperComponent={CustomPopper}
          options={
            showSelectAllOption
              ? [selectAllOption as T, ...sortedOptions]
              : sortedOptions
          }
          getOptionLabel={getOptionLabel}
          isOptionEqualToValue={isOptionEqualToValue}
          value={field.value ?? (multiple ? [] : null)}
          onChange={(_event, newVal, _, selectedOption) => {
            if (showSelectAllOption && selectedOption && multiple && Array.isArray(newVal)) {
              const isSelectAll =
                getOptionLabel(selectedOption?.option) ===
                selectAllOption?.name;
              const allOptionsSelected =
                newVal?.filter(
                  (o) => getOptionLabel(o) !== selectAllOption.name,
                ).length == sortedOptions?.length;

              if (isSelectAll && allOptionsSelected) {
                newVal = [];
              } else if (isSelectAll && !allOptionsSelected) {
                newVal = [selectAllOption as T, ...sortedOptions];
              } else if (!isSelectAll && !allOptionsSelected) {
                newVal = newVal.filter(
                  (o) => getOptionLabel(o) !== selectAllOption.name,
                );
              } else if (!isSelectAll && allOptionsSelected) {
                newVal = [selectAllOption as T, ...newVal];
              }
            }
            field.onChange(newVal);
            if (props.onChange) {
              props.onChange(_event, newVal, "selectOption");
            }
          }}
          multiple={multiple}
          disableCloseOnSelect={multiple}
          limitTags={multiple ? 1 : undefined}
          popupIcon={<ExpandMore />}
          renderTags={(value, getTagProps) => {
            if (
              showAllSelectedText &&
              multiple &&
              Array.isArray(value) &&
              sortedOptions.length > 0
            ) {
              const actualSelectedOptions = value.filter(
                (item) => getOptionLabel(item) !== selectAllOption.name,
              );
              if (actualSelectedOptions.length >= sortedOptions.length) {
                return [<span key="all-selected">All</span>];
              }
            }
            return value.map((option, index) => {
              const { onDelete, key, ...chipProps } = getTagProps({ index });

              return (
                <Chip
                  label={getOptionLabel(option)}
                  key={key}
                  {...chipProps}
                  onDelete={(e) => {
                    onDelete(e);
                    onDeleteOption?.(option);
                  }}
                />
              );
            });
          }}
          renderOption={(props, option, { selected }) => {
            const { key, ...otherProps } = props;
            const badge = renderOptionBadge ? renderOptionBadge(option) : null;

            return (
              <li key={key} {...otherProps}>
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    width: "100%",
                  }}
                >
                  <Box sx={{ display: "flex", alignItems: "center" }}>
                    {multiple && (
                      <Checkbox
                        icon={<CheckBoxOutlineBlank />}
                        checkedIcon={<CheckBox />}
                        checked={selected}
                      />
                    )}
                    {getOptionLabel(option)}
                  </Box>
                  {badge && (
                    <Chip
                      label={badge.label}
                      color={badge.color}
                      size="small"
                      sx={{ ml: 1 }}
                    />
                  )}
                </Box>
              </li>
            );
          }}
          renderInput={(params) => (
            <TextField
              {...params}
              label={label}
              placeholder={multiple && field?.value?.length ? "" : placeholder}
              name={name}
              error={!!errors[name]}
              helperText={String(errors[name]?.message ?? "")}
              InputLabelProps={{
                shrink: true, // for always display the placeholder
                sx: {
                  fontWeight: isRequired ? "bold" : "normal",
                },
              }}
            />
          )}
          ChipProps={
            multiple
              ? {
                  deleteIcon: <Close />,
                  onDelete: (chipProps) => {
                    if (onDeleteOption) {
                      const optionToDelete = field.value.find(
                        (item: T) =>
                          getOptionLabel(item) ===
                          chipProps.currentTarget.parentElement?.textContent,
                      );
                      if (optionToDelete) {
                        onDeleteOption(optionToDelete);
                      }
                    } else {
                      // Trigger default behavior by removing the chip
                      const chipToDelete =
                        chipProps.currentTarget.parentElement?.textContent;
                      field.onChange(
                        field.value.filter(
                          (item: T) => getOptionLabel(item) !== chipToDelete,
                        ),
                      );
                    }
                  },
                }
              : undefined
          }
        />
      )}
    />
  );
};

export default ControlledAutoComplete;
