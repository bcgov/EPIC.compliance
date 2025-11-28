import { Box, Typography, Button, Chip, Link } from "@mui/material";
import { SendRounded } from "@mui/icons-material";
import {
  APPROVAL_STATUS,
  InspectionStatusEnum,
  IRProgressEnum,
  STAFF_USER_POSITION,
  VARIANT_COLORS,
} from "@/utils/constants";
import { useMemo, useState, useEffect, useCallback } from "react";
import {
  useCreateIRApproval,
  useDeleteInspectionRecord,
  useUpdateIRApprovalStatus,
} from "@/hooks/useInspectionReports";
import { notify } from "@/store/snackbarStore";
import { useReportStore } from "./reportStore";
import { IRApproval } from "@/models/IRApproval";
import { useCurrentLoggedInUser } from "@/hooks/useAuthorization";
import { useStaffUsersData } from "@/hooks/useStaff";
import SendForApprovalModal, {
  SendForApprovalFormType,
} from "@/components/App/Inspections/Profile/SendForApprovalModal";
import { useModal } from "@/store/modalStore";
import OfficerStepper from "./OfficerSteppr/OfficerStepper";
import PreviewDownloadButton from "./PreviewDownloadButton";
import IssueIRModal from "./IssueIRModal";
import ReopenIRModal from "./ReopenIRModal";
import { StaffUser } from "@/models/Staff";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";

// Status badge configurations
const STATUS_BADGE_CONFIG = {
  PENDING: { text: "Approval Pending", color: "warning" },
  APPROVED: { text: "Approved", color: "success" },
  NOT_APPROVED: { text: "Not Approved", color: "error" },
  ISSUED: { text: "Issued", color: "success" },
  DEFAULT: { text: "", color: "default" },
};

export default function ReportTopSection() {
  const { setOpen, setClose } = useModal();
  const currentUser = useCurrentLoggedInUser();
  const [irApprStatusBadge, setIrApprStatusBadge] = useState(
    STATUS_BADGE_CONFIG.DEFAULT
  );

  const {
    queryClient,
    inspectionData,
    inspectionReportsData,
    irApprovalsData,
    isReportsReadOnly,
    isHistorical,
    setIRApprovalsData,
  } = useReportStore();

  const { data: staffData } = useStaffUsersData();
  const irProgressId = inspectionReportsData?.ir_progress?.id as IRProgressEnum;

  // Memoize the current user's staff ID
  const currentUserStaffId = useMemo(
    () =>
      staffData?.find(
        (staff) => staff.auth_user_guid === currentUser?.preferred_username
      )?.id ?? 0,
    [staffData, currentUser]
  );

  // Check if current user is an approver (director or deputy director)
  const isCurrentUserApprover = useMemo(() => {
    return staffData?.some(
      (staff) =>
        staff.auth_user_guid === currentUser?.preferred_username &&
        [
          STAFF_USER_POSITION.DEPUTY_DIRECTOR,
          STAFF_USER_POSITION.DIRECTOR,
        ].includes(staff.position_id ?? 0)
    );
  }, [staffData, currentUser]);

  const refetchInspectionReportsData = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: ["inspection-reports", inspectionData?.id],
    });
  }, [queryClient, inspectionData?.id]);

  // Callback for handling approval success
  const onApprovalSuccess = useCallback(
    (data: IRApproval) => {
      setIRApprovalsData([data]);
      notify.success("Approval status updated");
      refetchInspectionReportsData();
    },
    [setIRApprovalsData, refetchInspectionReportsData]
  );

  const { mutate: updateIRApprovalStatus } =
    useUpdateIRApprovalStatus(onApprovalSuccess);

  // Flag conditions
  const isInDeputyReview = useMemo(
    () =>
      [
        IRProgressEnum.PRELIMINARY_DEPUTY_REVIEW,
        IRProgressEnum.FINAL_DEPUTY_REVIEW,
      ].includes(irProgressId),
    [irProgressId]
  );

  const isInDraftingOrFinalizing = useMemo(
    () =>
      [
        IRProgressEnum.PRELIMINARY_DRAFTING,
        IRProgressEnum.FINALIZING_RECORD,
      ].includes(irProgressId),
    [irProgressId]
  );

  const isDisableApprovalButton = useMemo(
    () => isInDeputyReview && !isCurrentUserApprover,
    [isInDeputyReview, isCurrentUserApprover]
  );

  const isShowSendForApprovalButton = useMemo(
    () => isInDraftingOrFinalizing || isDisableApprovalButton,
    [isInDraftingOrFinalizing, isDisableApprovalButton]
  );

  const isShowApprovalButtons = useMemo(
    () => isInDeputyReview && isCurrentUserApprover,
    [isInDeputyReview, isCurrentUserApprover]
  );

  const isShowOfficerStepper = useMemo(
    () =>
      [
        IRProgressEnum.PRELIMINARY_APPROVED,
        IRProgressEnum.FINAL_APPROVED,
        IRProgressEnum.HOLDER_PRELIMINARY_REVIEW,
      ].includes(irProgressId),
    [irProgressId]
  );

  const isShowIssueIRButton = useMemo(
    () =>
      irProgressId === IRProgressEnum.FINAL_APPROVED &&
      inspectionReportsData?.intended_issuance_date,
    [irProgressId, inspectionReportsData?.intended_issuance_date]
  );

  const isShowReopenIRButton = useMemo(
    () =>
      irProgressId === IRProgressEnum.ISSUED &&
      inspectionData?.inspection_status === InspectionStatusEnum.OPEN,
    [irProgressId, inspectionData?.inspection_status]
  );

  const onSuccess = (data: IRApproval) => {
    setIRApprovalsData([data]);
    notify.success("Approval request sent");
    setClose();
    refetchInspectionReportsData();
  };

  const { mutate: createIRApproval, isPending } =
    useCreateIRApproval(onSuccess);

  const onSendForApprovalSubmitHandler = useCallback(
    (data: SendForApprovalFormType) => {
      const directorId = (data.director as StaffUser).id;
      createIRApproval({
        inspectionId: inspectionData?.id ?? 0,
        inspectionRecordId: inspectionReportsData?.id ?? 0,
        approvalPayload: {
          approved_by_id: directorId,
        },
      });
    },
    [createIRApproval, inspectionData, inspectionReportsData]
  );

  // Modal handlers
  const handleSendForApproval = useCallback(() => {
    setOpen({
      content: (
        <SendForApprovalModal
          staffUsers={staffData ?? []}
          onSubmitHandler={onSendForApprovalSubmitHandler}
          isPending={isPending}
        />
      ),
    });
  }, [setOpen, staffData, onSendForApprovalSubmitHandler, isPending]);

  const handleIssueIR = useCallback(() => {
    setOpen({
      content: (
        <IssueIRModal
          onSubmit={(message) => {
            notify.success(message);
            setClose();
            refetchInspectionReportsData();
            queryClient.invalidateQueries({
              queryKey: ["inspection", inspectionData?.ir_number],
            });
          }}
        />
      ),
    });
  }, [
    setOpen,
    setClose,
    refetchInspectionReportsData,
    queryClient,
    inspectionData,
  ]);

  const handleReopenIR = useCallback(() => {
    setOpen({
      content: (
        <ReopenIRModal
          onSubmit={(message) => {
            notify.success(message);
            setClose();
            refetchInspectionReportsData();
            queryClient.invalidateQueries({
              queryKey: ["inspection", inspectionData?.ir_number],
            });
          }}
        />
      ),
    });
  }, [
    setOpen,
    setClose,
    refetchInspectionReportsData,
    queryClient,
    inspectionData,
  ]);

  const handleApproval = useCallback(
    (isApprove: boolean) => {
      updateIRApprovalStatus({
        inspectionId: inspectionData?.id ?? 0,
        inspectionRecordId: inspectionReportsData?.id ?? 0,
        approvalId: irApprovalsData?.[0]?.id ?? 0,
        statusPayload: {
          approval_status: isApprove
            ? APPROVAL_STATUS.APPROVED
            : APPROVAL_STATUS.NOT_APPROVED,
          approved_by_id: currentUserStaffId,
        },
      });
    },
    [
      updateIRApprovalStatus,
      inspectionData?.id,
      inspectionReportsData?.id,
      irApprovalsData,
      currentUserStaffId,
    ]
  );

  // Determine status badge based on current state
  useEffect(() => {
    if (isInDeputyReview) {
      setIrApprStatusBadge(STATUS_BADGE_CONFIG.PENDING);
    } else if (isShowOfficerStepper) {
      setIrApprStatusBadge(STATUS_BADGE_CONFIG.APPROVED);
    } else if (
      isInDraftingOrFinalizing &&
      irApprovalsData?.[0]?.approval_status?.id === APPROVAL_STATUS.NOT_APPROVED
    ) {
      setIrApprStatusBadge(STATUS_BADGE_CONFIG.NOT_APPROVED);
    } else if (irProgressId === IRProgressEnum.ISSUED) {
      setIrApprStatusBadge(STATUS_BADGE_CONFIG.ISSUED);
    } else {
      setIrApprStatusBadge(STATUS_BADGE_CONFIG.DEFAULT);
    }
  }, [
    irProgressId,
    isInDeputyReview,
    isShowOfficerStepper,
    isInDraftingOrFinalizing,
    irApprovalsData,
  ]);

  const onDeleteInspectionRecordSuccess = useCallback(() => {
    setClose();
    refetchInspectionReportsData();
  }, [setClose, refetchInspectionReportsData]);

  const { mutate: deleteInspectionRecord } = useDeleteInspectionRecord(
    onDeleteInspectionRecordSuccess
  );

  const handleChangeIRVersion = useCallback(() => {
    setOpen({
      content: (
        <ConfirmationModal
          title="Change the Report Version?"
          description="Changing will delete the current version and return you to the version selection screen. This action cannot be undone."
          onConfirm={() => {
            deleteInspectionRecord({
              inspectionId: inspectionData?.id ?? 0,
              inspectionRecordId: inspectionReportsData?.id ?? 0,
            });
          }}
          confirmButtonText="Change"
        />
      ),
    });
  }, [setOpen, deleteInspectionRecord, inspectionData, inspectionReportsData]);

  return (
    <>
      <Box
        sx={{
          mb: 1,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <Box sx={{ display: "flex", flexDirection: "column" }}>
          <Box display={"flex"} gap={1} alignItems={"center"}>
            <Typography variant="h6">
              {inspectionReportsData?.ir_status?.name} IR
            </Typography>
            {irApprStatusBadge.text && (
              <Chip
                label={irApprStatusBadge.text}
                color={irApprStatusBadge.color as VARIANT_COLORS}
                variant="outlined"
                size="small"
              />
            )}
          </Box>
          {!isReportsReadOnly && !isHistorical && (
            <Box sx={{ display: "flex", alignItems: "center", gap: 0.5 }}>
              <Typography variant="body2">Wrong Version?</Typography>
              <Link
                underline="hover"
                sx={{ cursor: "pointer" }}
                onClick={handleChangeIRVersion}
              >
                Change
              </Link>
            </Box>
          )}
        </Box>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {!isReportsReadOnly && (
            <>
              {isShowSendForApprovalButton && !isHistorical && (
                <Button
                  variant="text"
                  color="primary"
                  onClick={handleSendForApproval}
                  disabled={isDisableApprovalButton}
                >
                  <SendRounded sx={{ mr: 0.5, fontSize: 20 }} />
                  Send for Approval
                </Button>
              )}
              {isShowApprovalButtons && !isHistorical && (
                <>
                  <Button
                    color="secondary"
                    size="small"
                    onClick={() => handleApproval(true)}
                  >
                    Approve
                  </Button>
                  <Button
                    color="secondary"
                    size="small"
                    onClick={() => handleApproval(false)}
                  >
                    Not Approve
                  </Button>
                </>
              )}
              {isShowIssueIRButton && (
                <Button onClick={handleIssueIR}>Issue IR</Button>
              )}
              {isShowReopenIRButton && (
                <Button onClick={handleReopenIR}>Reopen IR</Button>
              )}
            </>
          )}
          <PreviewDownloadButton />
        </Box>
      </Box>
      {isShowOfficerStepper && <OfficerStepper />}
    </>
  );
}
