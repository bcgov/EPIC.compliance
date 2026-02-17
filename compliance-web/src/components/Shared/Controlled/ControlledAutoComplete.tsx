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
} from "@mui/material";
import { useMemo } from "react";
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
  showAllSelectedText?: boolean;
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
  showAllSelectedText = false,
  ...props
}: FormAutocompleteProps<T>) => {
  const {
    control,
    formState: { errors, defaultValues },
  } = useFormContext();

  const sortedOptions = useMemo(() => {
    if (isSortOptions) {
      return options.sort((a, b) =>
        getOptionLabel(a).localeCompare(getOptionLabel(b)),
      );
    }
    return options;
  }, [isSortOptions, options, getOptionLabel]);

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
          options={sortedOptions}
          getOptionLabel={getOptionLabel}
          isOptionEqualToValue={isOptionEqualToValue}
          value={field.value ?? (multiple ? [] : null)}
          onChange={(_event, newVal) => {
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
              value.length === sortedOptions.length &&
              sortedOptions.length > 0
            ) {
              return [<span>All Selected</span>];
            }
            return value.map((option, index) => {
              const { onDelete, ...chipProps } = getTagProps({ index });

              return (
                <Chip
                  label={getOptionLabel(option)}
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
