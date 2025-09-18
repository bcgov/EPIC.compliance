import { Box, Button, SelectChangeEvent, Typography } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { AddRounded } from "@mui/icons-material";
import ContinuationReportTimeline from "./ContinuationReportTimeline";
import { useModal } from "@/store/modalStore";
import ContinuationReportEntryModal from "./ContinuationReportEntryModal";
import { notify } from "@/store/snackbarStore";
import { useContinuationReportEntries } from "@/hooks/useContinuationReports";
import LoadingPage from "@/components/Shared/LoadingPage";
import ErrorPage from "@/components/Shared/ErrorPage";
import { useQueryClient } from "@tanstack/react-query";
import { AppConfig } from "@/utils/config";
import ComingSoon from "@/components/Shared/ComingSoon";
import { useCallback, useEffect, useState } from "react";
import ContinuationReportPagination from "./ContinuationReportPagination";
import DynamicHeightBox from "@/components/Shared/DynamicHeightBox";
import SearchTextField from "@/components/Shared/SearchTextField";

export type ContinuationReportContextType = {
  caseFileId: number;
  contextType: string;
  contextId: number;
  allowCreateEntry?: boolean;
};

export default function ContinuationReport({
  caseFileId,
  contextType,
  contextId,
  allowCreateEntry,
}: ContinuationReportContextType) {
  const queryClient = useQueryClient();
  const { setOpen, setClose } = useModal();
  const [page, setPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchText, setSearchText] = useState("");
  const [debouncedSearchText, setDebouncedSearchText] = useState("");

  // Debounce effect
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchText(searchText);
    }, 300); // Adjust the delay as needed

    return () => {
      clearTimeout(handler); // Cleanup the timeout
    };
  }, [searchText]);

  const {
    status,
    data: continuationReportData,
    isError,
    error,
    isLoading,
  } = useContinuationReportEntries(
    caseFileId,
    page,
    rowsPerPage,
    debouncedSearchText
  );

  const handleOnSubmit = useCallback(
    (submitMsg: string) => {
      queryClient.invalidateQueries({
        queryKey: ["continuation-reports", caseFileId],
        exact: false,
      });
      setClose();
      notify.success(submitMsg);
    },
    [queryClient, caseFileId, setClose]
  );

  const handleAddNewEntry = useCallback(() => {
    setOpen({
      content: (
        <ContinuationReportEntryModal
          onSubmit={handleOnSubmit}
          context={{ caseFileId, contextType, contextId }}
        />
      ),
      width: "640px",
    });
  }, [setOpen, handleOnSubmit, caseFileId, contextType, contextId]);

  const handlePageChange = useCallback(
    (_event: React.ChangeEvent<unknown>, newPage: number) => {
      setPage(newPage);
    },
    []
  );

  const handleRowsPerPageChange = (event: SelectChangeEvent) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(1); // Reset to the first page when rows per page changes
  };

  return (
    <DynamicHeightBox
      width="40%"
      bgcolor={BCDesignTokens.surfaceColorBackgroundLightGray}
      p={3}
      pb={2}
      display="flex"
      flexDirection="column"
      bottomOffset={20} // 20px padding bottom of the parent component
    >
      {AppConfig.inprogressFeatures?.includes("CONTINUATION_REPORT") ? (
        <ComingSoon />
      ) : (
        <>
          <Box display={"flex"} justifyContent={"space-between"} mb={2}>
            <Typography variant="h6">Continuation Report</Typography>
            {allowCreateEntry && (
              <Button
                variant="text"
                color="primary"
                size="small"
                onClick={handleAddNewEntry}
                startIcon={<AddRounded />}
              >
                New Entry
              </Button>
            )}
          </Box>
          <SearchTextField
            id="searchTextField"
            value={searchText}
            onChange={(value) => {
              setSearchText(value);
            }}
          />
          {!caseFileId || status === "pending" ? (
            <LoadingPage isLoading={isLoading} />
          ) : isError ? (
            <ErrorPage error={error} hideBackButton />
          ) : continuationReportData.items.length ? (
            <>
              <Box
                sx={{
                  // height: `calc(100vh - ${appHeaderHeight + 302 + 48 + inspectionOffset}px)`, // 302px is the height above the timeline, 48px is height of pagination
                  overflow: "auto",
                  display: "flex",
                  flex: 1,
                  flexDirection: "column",
                }}
              >
                <ContinuationReportTimeline
                  crtList={continuationReportData.items}
                  searchText={debouncedSearchText}
                  isAllowEdit={allowCreateEntry}
                />
              </Box>
              <ContinuationReportPagination
                page={page}
                rowsPerPage={rowsPerPage}
                total={continuationReportData.total}
                onPageChange={handlePageChange}
                onRowsPerPageChange={handleRowsPerPageChange}
              />
            </>
          ) : (
            <Typography variant="subtitle2" textAlign={"center"} mt={4}>
              -- No Records --
            </Typography>
          )}
        </>
      )}
    </DynamicHeightBox>
  );
}
