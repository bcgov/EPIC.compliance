import {
  ArrowDropDownRounded,
  DownloadRounded,
  PictureAsPdfRounded,
} from "@mui/icons-material";
import {
  Button,
  ClickAwayListener,
  ButtonGroup,
  Grow,
  Paper,
  Popper,
  Typography,
  Link,
  Box,
  CircularProgress,
} from "@mui/material";
import { useMemo, useRef, useState } from "react";
import { useInspectionRecordRender } from "@/hooks/useInspectionReports";
import { useModal } from "@/store/modalStore";
import { useReportStore } from "./reportStore";
import ReportPreviewModal from "./ReportPreviewModal";
import { BCDesignTokens } from "epic.theme";
import {
  KC_USER_GROUPS,
  useCurrentLoggedInUser,
} from "@/hooks/useAuthorization";
import { useIsRolesAllowed } from "@/hooks/useAuthorization";
import { InspectionStatusEnum } from "@/utils/constants";
import { AxiosError } from "axios";
import { notify } from "@/store/snackbarStore";
import {
  useDeleteDocumentJobs,
  useLastGeneratedTimeForUser,
  useMostRecentDocumentJobForUser,
} from "@/hooks/useDocumentJobs";
import { DocumentJob, DocumentJobStatus } from "@/models/documentJob";
import dateUtils from "@/utils/dateUtils";
import { useFetchPresignedGetURL } from "@/hooks/useImageUpload";
import { useQueryClient } from "@tanstack/react-query";

const PreviewDownloadButton = () => {
  const { setOpen: setModalOpen } = useModal();
  const { inspectionData, inspectionReportsData } = useReportStore();

  const { data: documentJob } = useMostRecentDocumentJobForUser(
    inspectionReportsData?.id ?? 0,
    "docx"
  );

  const { data: lastGeneratedTimeObj } = useLastGeneratedTimeForUser(
    inspectionReportsData?.id ?? 0,
    "docx"
  );
  const lastGeneratedTime = lastGeneratedTimeObj?.last_generated_time;

  const [previewClicked, setPreviewClicked] = useState(false);
  const [open, setOpen] = useState(false);
  const anchorRef = useRef<HTMLDivElement>(null);
  const currentUser = useCurrentLoggedInUser();

  const isSuperUser = useIsRolesAllowed([KC_USER_GROUPS.SUPERUSER]);

  const isUserPrimary = useMemo(
    () =>
      inspectionData?.primary_officer?.auth_user_guid ===
      currentUser?.preferred_username,
    [inspectionData?.primary_officer, currentUser?.preferred_username]
  );

  const isInspectionOpen = useMemo(
    () => inspectionData?.inspection_status === InspectionStatusEnum.OPEN,
    [inspectionData]
  );

  const isDownloadAllowed = useMemo(
    () => isInspectionOpen && (isUserPrimary || isSuperUser),
    [isInspectionOpen, isUserPrimary, isSuperUser]
  );

  const onSuccess = (data: DocumentJob | { html: string }) => {
    if ("html" in data) {
      setModalOpen({
        content: <ReportPreviewModal previewHtml={data.html ?? ""} />,
        width: "744px",
      });
    }
    setPreviewClicked(false);
  };

  const onError = (error: AxiosError) => {
    notify.error(
      (error.response?.data as { message?: string })?.message ??
      "Error processing report"
    );
    setPreviewClicked(false);
  };

  const { mutate: mutateIrPreviewData } = useInspectionRecordRender(
    onSuccess,
    onError
  );

  const isGenerating = useMemo(() => {
    return documentJob?.status === DocumentJobStatus.IN_PROGRESS;
  }, [documentJob]);

  const isCompleted = useMemo(() => {
    return documentJob?.status === DocumentJobStatus.COMPLETED;
  }, [documentJob]);

  const handlePreviewClick = async () => {
    setPreviewClicked(true);
    mutateIrPreviewData({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      outputFormat: "html",
    });
  };

  const queryClient = useQueryClient();
  const { mutate: mutateDeleteDocumentJob } = useDeleteDocumentJobs();

  const handleGenerateDocx = async (event: MouseEvent) => {
    handleClose(event);

    // Generating a new report invalidates the previous one
    if (documentJob?.id) {
      mutateDeleteDocumentJob(documentJob.id, {
        onSuccess: () => {
          queryClient.invalidateQueries({
            queryKey: [
              "mostRecentDocumentJob",
              inspectionReportsData?.id,
              "docx",
            ],
          });
        },
      });
    }

    mutateIrPreviewData(
      {
        inspectionId: inspectionData?.id ?? 0,
        inspectionRecordId: inspectionReportsData?.id ?? 0,
        outputFormat: "docx",
      },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({
            queryKey: [
              "mostRecentDocumentJob",
              inspectionReportsData?.id,
              "docx",
            ],
          });
        },
      }
    );
  };

  const handleToggle = () => {
    setOpen((prevOpen) => !prevOpen);
  };

  const handleClose = (event: MouseEvent | TouchEvent) => {
    if (
      anchorRef.current &&
      anchorRef.current.contains(event.target as HTMLElement)
    ) {
      return;
    }

    setOpen(false);
  };

  const onPresignedUrlSuccess = async (data: { presigned_url: string }) => {
    try {
      const response = await fetch(data.presigned_url);
      const blob = await response.blob();
      const filename =
        documentJob?.download_name ||
        `${inspectionData?.ir_number || inspectionReportsData?.id || "report"}.docx`;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      // Keep the completed job around so the Download link stays enabled for
      // repeat downloads - it's only replaced when the user generates a new one.
    } catch (error) {
      notify.error("Failed to download DOCX report");
    }
    setOpen(false);
  };

  const { mutate: mutateFetchPresignedGetURL } = useFetchPresignedGetURL(
    onPresignedUrlSuccess
  );

  const handleDownloadReportFromURL = () => {
    if (documentJob?.relative_url) {
      mutateFetchPresignedGetURL(documentJob.relative_url);
    }
  };

  return (
    <>
      <ButtonGroup
        variant="outlined"
        ref={anchorRef}
        aria-label="Button group for preview and download"
        sx={{
          "& .MuiButtonBase-root": {
            padding: "0.25rem 0.75rem",
            height: "38px",
            color: BCDesignTokens.typographyColorPrimary,
          },
        }}
      >
        <Button
          variant="contained"
          color="secondary"
          onClick={handlePreviewClick}
          disabled={previewClicked}
        >
          <PictureAsPdfRounded sx={{ mr: 1, fontSize: 20 }} />
          {previewClicked ? "Loading..." : "Preview"}
        </Button>
        {isDownloadAllowed && (
          <Button
            aria-controls={open ? "split-button-menu" : undefined}
            aria-expanded={open ? "true" : undefined}
            aria-label="download report"
            aria-haspopup="menu"
            variant="contained"
            color="secondary"
            onClick={handleToggle}
            sx={{
              padding: "0.5rem 0 !important",
              minWidth: "2rem !important",
            }}
          >
            <ArrowDropDownRounded />
          </Button>
        )}
      </ButtonGroup>
      <Popper
        sx={{
          zIndex: 2,
        }}
        open={open}
        anchorEl={anchorRef.current}
        role={undefined}
        transition
        disablePortal
      >
        {({ TransitionProps, placement }) => (
          <Grow
            {...TransitionProps}
            style={{
              transformOrigin:
                placement === "bottom" ? "center top" : "center bottom",
            }}
          >
            <Paper elevation={3} sx={{ pt: 1, pb: 1 }}>
              <ClickAwayListener
                onClickAway={(e) => handleClose(e as MouseEvent)}
              >
                <Box
                  sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-start",
                    gap: 1,
                  }}
                >
                  <Button
                    variant="text"
                    onClick={(e) =>
                      handleGenerateDocx(e as unknown as MouseEvent)
                    }
                    disabled={isGenerating}
                    fullWidth
                    sx={{ justifyContent: "flex-start" }}
                  >
                    <DownloadRounded sx={{ mr: 1, fontSize: 20 }} />
                    {isGenerating
                      ? "Generating DOCX..."
                      : "Generate Report as DOCX"}
                    {isGenerating && (
                      <CircularProgress
                        size={20}
                        color="primary"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Button>
                  <Box
                    sx={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-end",
                      gap: 1,
                      width: "100%",
                    }}
                  >
                    <Box
                      sx={{
                        display: "flex",
                        flexDirection: "column",
                        gap: 0.25,
                        pl: 2,
                      }}
                    >
                      {isCompleted || lastGeneratedTime ? (
                        <>
                          <Typography
                            variant="caption"
                            color={BCDesignTokens.typographyColorPlaceholder}
                          >
                            Last DOCX Generated:
                          </Typography>
                          <Typography
                            variant="caption"
                            color={BCDesignTokens.typographyColorPrimary}
                          >
                            {dateUtils.formatDate(
                              isCompleted
                                ? (documentJob?.completed_at ?? "")
                                : (lastGeneratedTime ?? ""),
                              "MMM D, YYYY hh:mm A"
                            )}
                          </Typography>
                        </>
                      ) : (
                        <Typography
                          variant="caption"
                          color={BCDesignTokens.typographyColorPlaceholder}
                        >
                          Nothing generated yet
                        </Typography>
                      )}
                    </Box>
                    <Link
                      onClick={
                        isCompleted ? handleDownloadReportFromURL : () => {}
                      }
                      sx={{
                        display: "flex",
                        alignItems: "flex-end",
                        pr: 2,
                        fontSize: 14,
                        color: isCompleted ? "primary" : "text.disabled",
                        pointerEvents: isCompleted ? "auto" : "none",
                        cursor: isCompleted ? "pointer" : "not-allowed",
                      }}
                    >
                      <DownloadRounded sx={{ fontSize: 16 }} />
                      Download
                    </Link>
                  </Box>
                </Box>
              </ClickAwayListener>
            </Paper>
          </Grow>
        )}
      </Popper>
    </>
  );
};

export default PreviewDownloadButton;
