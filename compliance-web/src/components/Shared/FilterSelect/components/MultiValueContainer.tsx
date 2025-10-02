import { components, MultiValueProps } from "react-select";
import { Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";

const MultiValue = ({ selectProps, index, ...props }: MultiValueProps) => {
  const { filterProps, value, placeholder } = selectProps;
  const selectedValue = Array.isArray(value) ? value : [value];
  const hasSelectedValue = selectedValue.length > 0;
  return (
    <components.MultiValueContainer {...props} selectProps={selectProps}>
      {index === 0 && (
        <Typography
          key={index}
          variant="body2"
          align="left"
          sx={{
            overflow: "hidden",
            textOverflow: "ellipsis",
            fontWeight: hasSelectedValue
              ? BCDesignTokens.typographyFontWeightsBold
              : undefined,
            color: hasSelectedValue
              ? BCDesignTokens.themeBlue80
              : filterProps?.variant === "inline-standalone"
                ? BCDesignTokens.typographyColorPrimary
                : BCDesignTokens.typographyColorPlaceholder,
          }}
        >
          {hasSelectedValue
            ? filterProps?.variant === "inline"
              ? "Filtered"
              : `${placeholder}`
            : placeholder}
        </Typography>
      )}
    </components.MultiValueContainer>
  );
};

export default MultiValue;
