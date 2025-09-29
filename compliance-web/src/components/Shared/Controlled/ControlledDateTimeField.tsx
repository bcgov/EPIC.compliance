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
  useCurrentTimeOnEmpty?: boolean;
} & DatePickerProps<Dayjs>;

const ControlledDateTimeField: FC<IFormDateInputProps> = ({
  name,
  placeHolder = DATE_FORMAT,
  isRequired = false,
  width = "100%",
  useCurrentTimeOnEmpty = false,
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
    if (value === "") return "";
    const numValue = typeof value === "number" ? value : parseInt(value.toString());
    return numValue.toString().padStart(2, "0");
  };

  const [hour, setHour] = useState(dateValue ? formatTimeValue(dateValue.hour()) : "");
  const [minute, setMinute] = useState(dateValue ? formatTimeValue(dateValue.minute()) : "");

  // Sync local state with field value when it changes externally
  useEffect(() => {
    if (fieldValue) {
      const date = dayjs(fieldValue);
      if (useCurrentTimeOnEmpty) {
        const now = dayjs();
        const storedHour = date.hour();
        const storedMinute = date.minute();
        const currentHour = now.hour();
        const currentMinute = now.minute();
        
        if (storedHour !== currentHour || storedMinute !== currentMinute) {
          setHour(formatTimeValue(storedHour));
          setMinute(formatTimeValue(storedMinute));
        } else {
          setHour("");
          setMinute("");
        }
      } else {
        setHour(formatTimeValue(date.hour()));
        setMinute(formatTimeValue(date.minute()));
      }
    }
  }, [fieldValue, useCurrentTimeOnEmpty]);

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

          let hourNum: number;
          let minuteNum: number;

          if (useCurrentTimeOnEmpty && newHour === "" && newMinute === "") {
            const now = dayjs();
            hourNum = now.hour();
            minuteNum = now.minute();
          } else {

            if (newHour === "") {
              hourNum = 0;
            } else if (typeof newHour === "string") {
              hourNum = parseInt(newHour);
            } else {
              hourNum = newHour;
            }
            if (newMinute === "") {
              minuteNum = 0;
            } else if (typeof newMinute === "string") {
              minuteNum = parseInt(newMinute);
            } else {
              minuteNum = newMinute;
            }
          }

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
                    if (useCurrentTimeOnEmpty) {
                      const dateHour = date.hour();
                      const dateMinute = date.minute();
                      const now = dayjs();
                      const currentHour = now.hour();
                      const currentMinute = now.minute();
                      
                      if (dateHour !== currentHour || dateMinute !== currentMinute) {
                        setHour(formatTimeValue(dateHour));
                        setMinute(formatTimeValue(dateMinute));
                      } else {
                        setHour("");
                        setMinute("");
                      }
                    } else {
                      const currentHour = date.hour();
                      const currentMinute = date.minute();
                      
                      setHour(currentHour === 0 ? "" : formatTimeValue(currentHour));
                      setMinute(currentMinute === 0 ? "" : formatTimeValue(currentMinute));
                    }
                    
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
                    setHour("");
                    if (field.value) {
                      updateDateTime(dayjs(field.value), "", minute);
                    }
                  } else {
                    const hourNum = parseInt(e.target.value);
                    if (!isNaN(hourNum) && hourNum >= 0) {
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
                    setMinute("");
                    if (field.value) {
                      updateDateTime(dayjs(field.value), hour, "");
                    }
                  } else {
                    const minuteNum = parseInt(e.target.value);
                    if (!isNaN(minuteNum) && minuteNum >= 0) {
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
