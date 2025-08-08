import { Complaint } from "@/models/Complaint";
import { ChevronLeftRounded, ChevronRightRounded } from "@mui/icons-material";
import { Box, Typography, IconButton } from "@mui/material";
import { MRT_TableInstance } from "material-react-table";

interface ComplaintsGridPaginationProps {
  table: MRT_TableInstance<Complaint>;
  totalCount: number;
}

export default function ComplaintsGridPagination({
  table,
  totalCount,
}: ComplaintsGridPaginationProps) {
  const currentPage = table.getState().pagination.pageIndex;
  const pageSize = table.getState().pagination.pageSize;
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
        onClick={() => table.previousPage()}
        disabled={!table.getCanPreviousPage()}
      >
        <ChevronLeftRounded fontSize="small" />
      </IconButton>
      <IconButton
        aria-label="page_forward"
        size="small"
        onClick={() => table.nextPage()}
        disabled={!table.getCanNextPage()}
      >
        <ChevronRightRounded fontSize="small" />
      </IconButton>
    </Box>
  );
} 
