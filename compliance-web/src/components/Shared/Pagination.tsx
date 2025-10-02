import { ChevronLeftRounded, ChevronRightRounded } from "@mui/icons-material";
import { Box, Typography, IconButton } from "@mui/material";

export interface PaginationProps {
  currentPage: number;
  pageSize: number;
  totalCount: number;
  onPreviousPage: () => void;
  onNextPage: () => void;
  canPreviousPage: boolean;
  canNextPage: boolean;
}

export default function Pagination({
  currentPage,
  pageSize,
  totalCount,
  onPreviousPage,
  onNextPage,
  canPreviousPage,
  canNextPage,
}: PaginationProps) {
  const startItem = currentPage * pageSize + 1;
  const endItem = Math.min((currentPage + 1) * pageSize, totalCount);

  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        gap: 0.5,
        justifyContent: "center",
      }}
    >
      <Typography variant="body1">
        {startItem} to {endItem} of {totalCount}
      </Typography>
      <IconButton
        aria-label="page_back"
        size="small"
        onClick={onPreviousPage}
        disabled={!canPreviousPage}
      >
        <ChevronLeftRounded fontSize="small" />
      </IconButton>
      <IconButton
        aria-label="page_forward"
        size="small"
        onClick={onNextPage}
        disabled={!canNextPage}
      >
        <ChevronRightRounded fontSize="small" />
      </IconButton>
    </Box>
  );
}
