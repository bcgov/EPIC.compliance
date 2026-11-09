import { useState, useCallback, memo, useEffect } from "react";
import { DatePicker } from "@mui/x-date-pickers/DatePicker";
import { IconButton, Tooltip, InputAdornment } from "@mui/material";
import { ClearRounded } from "@mui/icons-material";
import { Dayjs } from "dayjs";
import { BCDesignTokens } from "epic.theme";
import { DATE_FORMAT } from "@/utils/constants";
import { MRT_Column, MRT_Header, MRT_RowData } from "material-react-table";
import dayjs from "dayjs";

interface DateFilterProps {
  header: MRT_Header<MRT_RowData>;
  column: MRT_Column<MRT_RowData>;
  placeholder?: string;
}

const DateFilter = memo(
  ({ header, placeholder = "Filter" }: DateFilterProps) => {
    const [value, setValue] = useState<Dayjs | null>(null);
    const [open, setOpen] = useState(false);

    const filterValue = header.column.getFilterValue() as string | undefined;
    useEffect(() => {
      setValue((prev) => {
        if (!filterValue) return null;
        // Keep the picker's own value when it already matches, so a date
        // being typed is not replaced mid-entry.
        if (prev && prev.format(DATE_FORMAT) === filterValue) return prev;
        return dayjs(filterValue, DATE_FORMAT);
      });
    }, [filterValue]);

    const handleDateChange = useCallback(
      (date: Dayjs | null) => {
        setValue(date);
        if (date) {
          header.column.setFilterValue(date.format(DATE_FORMAT));
        } else {
          header.column.setFilterValue("");
        }
      },
      [header.column]
    );

    const handleClear = useCallback(
      (event: React.MouseEvent<HTMLButtonElement>) => {
        event.stopPropagation();
        setValue(null);
        header.column.setFilterValue("");
      },
      [header.column, setValue]
    );

    const handleInputClick = useCallback(() => {
      setOpen(true);
    }, []);

    const handleClose = useCallback(() => {
      setOpen(false);
    }, []);

    return (
      <DatePicker
        value={value}
        onChange={handleDateChange}
        format={DATE_FORMAT}
        open={open}
        onClose={handleClose}
        slotProps={{
          textField: {
            placeholder,
            variant: "outlined",
            size: "small",
            onClick: handleInputClick,
            InputProps: {
              endAdornment: value ? (
                <InputAdornment position="end">
                  <Tooltip title="Clear filter">
                    <IconButton
                      size="small"
                      onClick={handleClear}
                      sx={{
                        height: "1.5rem",
                        width: "1.5rem",
                        color: BCDesignTokens.typographyColorPlaceholder,
                        "&:hover": {
                          color: BCDesignTokens.typographyColorPrimary,
                        },
                      }}
                    >
                      <ClearRounded fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </InputAdornment>
              ) : undefined,
            },
            sx: {
              backgroundColor: BCDesignTokens.surfaceColorBackgroundWhite,
              mb: 0,
              "& .MuiOutlinedInput-root": {
                height: "2.25rem",
                minHeight: "2.25rem",
                fontSize: BCDesignTokens.typographyFontSizeSmallBody,
              },
            },
          },
        }}
      />
    );
  }
);

DateFilter.displayName = "DateFilter";

export default DateFilter;
