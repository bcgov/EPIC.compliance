import { FC, useState, useEffect } from "react";
import { Controller, useFormContext } from "react-hook-form";
import dayjs, { Dayjs } from "dayjs";
import { Box, TextField, TextFieldProps, Stack } from "@mui/material";
import { DATE_FORMAT } from "@/utils/constants";
import { DatePicker, DatePickerProps } from "@mui/x-date-pickers";

type IFormDateInputProps = {
  name: string;
  placeHolder?: string;
  width?: string;
  isRequired?: boolean;
} & DatePickerProps<Dayjs>;

const ControlledDateTimeField: FC<IFormDateInputProps> = ({
  name,
  placeHolder = DATE_FORMAT,
  isRequired = false,
  width = "100%",
  ...otherProps
}) => {
  const {
    control,
    formState: { errors },
    watch,
  } = useFormContext();

  const fieldValue = watch(name);
  const dateValue = fieldValue ? dayjs(fieldValue) : null;
  // Format function to add leading zeros
  const formatTimeValue = (value: number | string): string => {
    if (value === 0 || value === "") return "";
    return typeof value === "number" ? value.toString().padStart(2, "0") : value;
  };

  const [hour, setHour] = useState(dateValue && dateValue.hour() !== 0 ? formatTimeValue(dateValue.hour()) : "");
  const [minute, setMinute] = useState(dateValue && dateValue.minute() !== 0 ? formatTimeValue(dateValue.minute()) : "");

  // Sync local state with field value when it changes externally
  useEffect(() => {
    if (fieldValue) {
      const date = dayjs(fieldValue);
      setHour(date.hour() === 0 ? "" : formatTimeValue(date.hour()));
      setMinute(date.minute() === 0 ? "" : formatTimeValue(date.minute()));
    }
  }, [fieldValue]);

  return (
    <Controller
      name={name}
      control={control}
      defaultValue={null}
      render={({ field }) => {
        // Update the combined date value whenever date, hour, or minute changes
        const updateDateTime = (
          newDate: Dayjs | null,
          newHour: number | string = hour,
          newMinute: number | string = minute
        ) => {
          if (!newDate) {
            field.onChange(null);
            return;
          }

          // Allow empty values in hour/minute fields
          const hourNum = newHour === "" ? 0 : 
            typeof newHour === "string" ? parseInt(newHour) : newHour;
          const minuteNum = newMinute === "" ? 0 :
            typeof newMinute === "string" ? parseInt(newMinute) : newMinute;

          // Only proceed if we have valid numbers
          if (!isNaN(hourNum) && !isNaN(minuteNum)) {
            const updatedDate = newDate
              .hour(Math.min(23, Math.max(0, hourNum)))
              .minute(Math.min(59, Math.max(0, minuteNum)));
            field.onChange(updatedDate);
          } else {
            // If hour/minute are invalid, just update the date part
            field.onChange(newDate);
          }
        };

        return (
          <Stack direction="row" spacing={2} width={width}>
            <Box width={"50%"}>
              <DatePicker
                {...field}
                label="Date"
                format={DATE_FORMAT}
                value={field.value ? dayjs(field.value) : null}
                onChange={(date: Dayjs | null) => {
                  if (date) {
                    // Get current hour and minute from the date
                    const currentHour = date.hour();
                    const currentMinute = date.minute();
                    
                    // Set empty string for 0 values, format others with padding
                    setHour(currentHour === 0 ? "" : formatTimeValue(currentHour));
                    setMinute(currentMinute === 0 ? "" : formatTimeValue(currentMinute));
                    
                    updateDateTime(date);
                  } else {
                    field.onChange(null);
                    setHour("");
                    setMinute("");
                  }
                }}
                slotProps={{
                  textField: {
                    error: !!errors[name],
                    helperText: errors[name]
                      ? String(errors[name]?.message)
                      : "",
                    placeholder: placeHolder,
                    InputLabelProps: {
                      shrink: true,
                      sx: {
                        fontWeight: isRequired ? "bold" : "normal",
                      },
                    },
                  } as TextFieldProps,
                }}
                {...otherProps}
              />
            </Box>
            <Box width={"25%"}>
              <TextField
                label="Hour (0-23)"
                type="number"
                fullWidth
                value={hour}
                inputProps={{
                  min: 0,
                  max: 23,
                  inputMode: "numeric",
                  pattern: "[0-9]*",
                  maxLength: 2,
                }}
                InputLabelProps={{
                  sx: {
                    maxWidth: "100%",
                  },
                }}
                onChange={(e) => {
                  let newHour = e.target.value;
                  // Allow empty value for backspace/clear operations
                  
                  // If input is not empty and is a valid number
                  if (newHour !== "") {
                    const hourNum = parseInt(newHour);
                    if (isNaN(hourNum)) {
                      // Don't update if not a number, but allow clearing
                      return;
                    } else if (hourNum > 23) {
                      newHour = "23";
                    } else if (hourNum < 0) {
                      newHour = "0";
                    }
                    
                    // Don't format during editing to allow proper input flow
                    setHour(newHour);
                  } else {
                    setHour("");
                  }
                  
                  if (field.value) {
                    updateDateTime(dayjs(field.value), newHour, minute);
                  }
                }}
                onBlur={(e) => {
                  // Format on blur for padding zeros
                  if (e.target.value === "") {
                    if (field.value) {
                      updateDateTime(dayjs(field.value), 0, minute);
                    }
                  } else {
                    const hourNum = parseInt(e.target.value);
                    if (!isNaN(hourNum) && hourNum > 0) {
                      // Apply padding only on blur
                      setHour(formatTimeValue(hourNum));
                    }
                  }
                }}
              />
            </Box>
            <Box width={"25%"}>
              <TextField
                label="Minute (0-59)"
                type="number"
                fullWidth
                value={minute}
                inputProps={{ 
                  min: 0,
                  max: 59,
                  inputMode: "numeric",
                  pattern: "[0-9]*",
                  maxLength: 2,
                }}
                InputLabelProps={{
                  sx: {
                    maxWidth: "100%",
                  },
                }}
                onChange={(e) => {
                  let newMinute = e.target.value;
                  // Allow empty value for backspace/clear operations
                  
                  // If input is not empty and is a valid number
                  if (newMinute !== "") {
                    const minuteNum = parseInt(newMinute);
                    if (isNaN(minuteNum)) {
                      // Don't update if not a number, but allow clearing
                      return;
                    } else if (minuteNum > 59) {
                      newMinute = "59";
                    } else if (minuteNum < 0) {
                      newMinute = "0";
                    }
                    
                    // Don't format during editing to allow proper input flow
                    setMinute(newMinute);
                  } else {
                    setMinute("");
                  }
                  
                  if (field.value) {
                    updateDateTime(dayjs(field.value), hour, newMinute);
                  }
                }}
                onBlur={(e) => {
                  // Format on blur for padding zeros
                  if (e.target.value === "") {
                    if (field.value) {
                      updateDateTime(dayjs(field.value), hour, 0);
                    }
                  } else {
                    const minuteNum = parseInt(e.target.value);
                    if (!isNaN(minuteNum) && minuteNum > 0) {
                      // Apply padding only on blur
                      setMinute(formatTimeValue(minuteNum));
                    }
                  }
                }}
              />
            </Box>
          </Stack>
        );
      }}
    />
  );
};

export default ControlledDateTimeField;
