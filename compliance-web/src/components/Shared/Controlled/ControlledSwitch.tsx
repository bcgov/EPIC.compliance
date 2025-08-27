import { FormControlLabel, SxProps } from "@mui/material";
import { FC } from "react";
import { Controller, useFormContext } from "react-hook-form";
import CustomSwitch from "./CustomSwitch";

type IFormSwitchProps = {
  name: string;
  label: string;
  isRequired?: boolean;
  sx?: SxProps;
};

const ControlledSwitch: FC<IFormSwitchProps> = ({
  name,
  label,
  isRequired = false,
  sx,
}) => {
  const { control } = useFormContext();
  return (
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <FormControlLabel
          style={{
            marginLeft: 0,
            fontWeight: isRequired ? "bold" : "normal",
          }}
          sx={sx}
          control={
            <CustomSwitch
              {...field}
              checked={field.value ?? false}
              value={field.value}
              onChange={(event) => field.onChange(event.target.checked)}
            />
          }
          label={label}
        />
      )}
    />
  );
};

export default ControlledSwitch;
