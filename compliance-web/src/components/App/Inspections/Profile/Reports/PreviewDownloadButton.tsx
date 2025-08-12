import { downloadFile } from "@/utils/appUtils";
import {
  ArrowDropDownRounded,
  DownloadRounded,
  PictureAsPdfOutlined,
} from "@mui/icons-material";
import {
  Button,
  ClickAwayListener,
  ButtonGroup,
  Grow,
  Paper,
  Popper,
  MenuList,
  MenuItem,
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

const PreviewDownloadButton = () => {
  const { setOpen: setModalOpen } = useModal();
  const { inspectionData, inspectionReportsData } = useReportStore();
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

  const onSuccess = (data: { html: string } | Blob) => {
    if ("html" in data) {
      setModalOpen({
        content: <ReportPreviewModal previewHtml={data.html ?? ""} />,
        width: "660px",
      });
    } else {
      downloadFile(data, `${inspectionData?.ir_number}.pdf`);
    }
    setPreviewClicked(false);
  };

  const onError = (error: AxiosError) => {
    notify.error(error.message ?? "Error processing report");
    setPreviewClicked(false);
  };

  const { mutate: mutateIrPreviewData } = useInspectionRecordRender(
    onSuccess,
    onError
  );

  const handlePreviewClick = async () => {
    setPreviewClicked(true);
    mutateIrPreviewData({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      outputFormat: "html",
    });
  };

  const handleDownloadClick = async (event: MouseEvent) => {
    setPreviewClicked(true);
    handleClose(event);
    mutateIrPreviewData({
      inspectionId: inspectionData?.id ?? 0,
      inspectionRecordId: inspectionReportsData?.id ?? 0,
      outputFormat: "pdf",
    });
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
        <Button onClick={handlePreviewClick} disabled={previewClicked}>
          <PictureAsPdfOutlined sx={{ mr: 1, fontSize: 20 }} />
          {previewClicked ? "Loading..." : "Preview"}
        </Button>
        {isDownloadAllowed && (
          <Button
            aria-controls={open ? "split-button-menu" : undefined}
            aria-expanded={open ? "true" : undefined}
            aria-label="download report"
            aria-haspopup="menu"
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
          zIndex: 1,
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
            <Paper>
              <ClickAwayListener onClickAway={handleClose}>
                <MenuList id="split-button-menu" autoFocusItem>
                  <MenuItem
                    key="download-report-as-pdf"
                    onClick={(e) =>
                      handleDownloadClick(e as unknown as MouseEvent)
                    }
                    disabled={previewClicked}
                    component="button"
                  >
                    <DownloadRounded sx={{ mr: 1, fontSize: 20 }} />
                    {previewClicked
                      ? "Downloading..."
                      : "Download Report as PDF"}
                  </MenuItem>
                </MenuList>
              </ClickAwayListener>
            </Paper>
          </Grow>
        )}
      </Popper>
    </>
  );
};

export default PreviewDownloadButton;
