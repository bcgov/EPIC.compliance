import { FC } from "react";
import { Controller, useFormContext } from "react-hook-form";
import { DatePicker, DatePickerProps } from "@mui/x-date-pickers";
import { Dayjs } from "dayjs";
import { TextFieldProps } from "@mui/material";
import { DATE_FORMAT } from "@/utils/constants";

type IFormDateInputProps = {
  name: string;
  label: string;
  placeHolder?: string;
  isRequired?: boolean;
  height?: string;
  width?: string;
} & DatePickerProps<Dayjs>;

const ControlledDateField: FC<IFormDateInputProps> = ({
  name,
  label,
  placeHolder = DATE_FORMAT,
  isRequired = false,
  height = "40px",
  width = "100%",
  ...otherProps
}) => {
  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <DatePicker
          {...field}
          label={label}
          format={DATE_FORMAT}
          value={field.value ?? null}
          onChange={(date: Dayjs | null) => {
            field.onChange(date);
            // Picking from the calendar never blurs the input, so forms in
            // onBlur mode would not recompute isValid until another field blurs
            field.onBlur();
          }}
          slotProps={{
            ...{
              textField: {
                error: !!errors[name],
                helperText: errors[name] ? String(errors[name]?.message) : "",
                placeholder: placeHolder,
                InputLabelProps: {
                  shrink: true, // for always display the placeholder
                  sx: {
                    fontWeight: isRequired ? "bold" : "normal",
                  },
                },
                sx: {
                  "& .MuiOutlinedInput-root": {
                    paddingRight: "0",
                    height: height,
                    width: width,
                    "& .MuiOutlinedInput-input": {
                      paddingRight: "0",
                    },
                    "& .MuiInputAdornment-positionEnd": {
                      "& .MuiIconButton-root": {
                        marginRight: "0",
                      },
                    },
                  },
                  width: "100%",
                },
              } as TextFieldProps,
            },
          }}
          {...otherProps}
        />
      )}
    />
  );
};

export default ControlledDateField;
