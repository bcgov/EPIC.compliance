import {
  TextField,
  InputAdornment,
  TextFieldProps,
} from "@mui/material";
import { CloseRounded, SearchRounded } from "@mui/icons-material";

export interface SearchTextFieldProps extends Omit<TextFieldProps, 'onChange'> {
  /**
   * The current search value
   */
  value: string;
  /**
   * Callback fired when the search value changes
   */
  onChange: (value: string) => void;
  /**
   * Callback fired when the clear button is clicked
   */
  onClear?: () => void;
  /**
   * Whether to show the search icon
   * @default true
   */
  showSearchIcon?: boolean;
  /**
   * Whether to show the clear button when there's text
   * @default true
   */
  showClearButton?: boolean;
}

/**
 * A reusable search text field component with search and clear icons
 */
export default function SearchTextField({
  value,
  onChange,
  onClear,
  showSearchIcon = true,
  showClearButton = true,
  placeholder = "Search",
  variant = "outlined",
  size = "small",
  ...props
}: SearchTextFieldProps) {
  const handleChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    onChange(event.target.value);
  };

  const handleClear = () => {
    onChange("");
    onClear?.();
  };

  const endAdornment = () => {
    if (value && showClearButton) {
      return (
        <CloseRounded
          fontSize="small"
          sx={{ cursor: "pointer" }}
          onClick={handleClear}
        />
      );
    }
    if (showSearchIcon) {
      return <SearchRounded />;
    }
    return null;
  };

  return (
    <TextField
      {...props}
      variant={variant}
      size={size}
      placeholder={placeholder}
      value={value}
      onChange={handleChange}
      InputProps={{
        ...props.InputProps,
        endAdornment: (
          <InputAdornment position="end">
            {endAdornment()}
          </InputAdornment>
        ),
      }}
    />
  );
}
