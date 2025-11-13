import { useStaffUsersData } from "@/hooks/useStaff";
import { SendRounded } from "@mui/icons-material";
import { Box, Button } from "@mui/material";
import { SendForApprovalFormType } from "@/components/App/Inspections/Profile/SendForApprovalModal";
import { useCallback, useMemo } from "react";
import SendForApprovalModal from "@/components/App/Inspections/Profile/SendForApprovalModal";
import { notify } from "@/store/snackbarStore";
import { useModal } from "@/store/modalStore";
import { StaffUser } from "@/models/Staff";
import { WarningLetterApproval } from "@/models/WarningLetterApproval";
import { useCurrentLoggedInUser } from "@/hooks/useAuthorization";
import {
  APPROVAL_STATUS,
  STAFF_USER_POSITION,
  WarningLetterProgressEnum,
} from "@/utils/constants";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import { useQueryClient } from "@tanstack/react-query";
import IssueEnforcementModal from "@/components/App/Inspections/Profile/Enforcements/IssueEnforcementModal";
import { useDrawer } from "@/store/drawerStore";
import { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import {
  useCreateWarningLetterApproval,
  useFetchWarningLetterApprovals,
  useUpdateWarningLetterApprovalStatus,
  useInspectionWarningLettersData,
} from "@/hooks/useInspectionWarningLetters";

const WarningLetterApprovalButtons = ({
  warningLetter,
  inspectionId,
}: {
  warningLetter: InspectionWarningLetter;
  inspectionId: number;
}) => {
  const { setOpen, setClose } = useModal();
  const { setClose: setDrawerClose } = useDrawer();
  const { data: staffData } = useStaffUsersData();
  const currentUser = useCurrentLoggedInUser();
  const queryClient = useQueryClient();
  
  // Get the latest warning letter data from cache to ensure buttons update immediately
  const { data: warningLettersData } = useInspectionWarningLettersData(inspectionId);
  const latestWarningLetter = useMemo(() => {
    return warningLettersData?.find(wl => wl.id === warningLetter.id) || warningLetter;
  }, [warningLettersData, warningLetter]);

  const { data: warningLetterApprovalsData } = useFetchWarningLetterApprovals(
    latestWarningLetter.id ?? 0
  );

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

  const refetchDataAndClose = useCallback(
    (message: string) => {
      notify.success(message);
      queryClient.invalidateQueries({
        queryKey: ["inspection-warning-letters", inspectionId],
      });
      setClose();
      setDrawerClose();
    },
    [queryClient, inspectionId, setClose, setDrawerClose]
  );

  const onSuccess = useCallback(
    (data: WarningLetterApproval) => {
      queryClient.setQueryData(
        ["warning-letter-approvals", latestWarningLetter.id],
        (oldData: WarningLetterApproval[]) => {
          return [...oldData, data];
        }
      );
      refetchDataAndClose("Approval request sent");
    },
    [refetchDataAndClose, queryClient, latestWarningLetter.id]
  );

  const { mutate: createWarningLetterApproval, isPending } =
    useCreateWarningLetterApproval(onSuccess);

  const onApprovalSuccess = useCallback(
    (data: WarningLetterApproval) => {
      notify.success("Approval status updated");
      queryClient.setQueryData(
        ["warning-letter-approvals", latestWarningLetter.id],
        (oldData: WarningLetterApproval[]) => {
          return oldData.map((approval) =>
            approval.id === data.id ? data : approval
          );
        }
      );
      refetchDataAndClose("Approval status updated");
    },
    [latestWarningLetter.id, queryClient, refetchDataAndClose]
  );

  const { mutate: updateWarningLetterApprovalStatus } =
    useUpdateWarningLetterApprovalStatus(onApprovalSuccess);

  const onSendForApprovalSubmitHandler = useCallback(
    (data: SendForApprovalFormType) => {
      const directorId = (data.director as StaffUser).id;
      createWarningLetterApproval({
        inspectionWarningLetterId: latestWarningLetter.id ?? 0,
        approvalPayload: {
          approved_by_id: directorId,
        },
      });
    },
    [createWarningLetterApproval, latestWarningLetter.id]
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

  const isInDeputyReview = useMemo(
    () =>
      latestWarningLetter.progress?.id === WarningLetterProgressEnum.DEPUTY_REVIEW,
    [latestWarningLetter.progress]
  );

  const isInDrafting = useMemo(
    () => latestWarningLetter.progress?.id === WarningLetterProgressEnum.DRAFTING,
    [latestWarningLetter.progress]
  );

  const isDisableSendApprovalButton = useMemo(
    () => isInDeputyReview && !isCurrentUserApprover,
    [isInDeputyReview, isCurrentUserApprover]
  );

  const isShowSendForApprovalButton = useMemo(
    () => isInDrafting || isDisableSendApprovalButton,
    [isInDrafting, isDisableSendApprovalButton]
  );

  const isShowApprovalButtons = useMemo(
    () => isInDeputyReview && isCurrentUserApprover,
    [isInDeputyReview, isCurrentUserApprover]
  );

  const isShowIssueButton = useMemo(
    () => latestWarningLetter?.progress?.id === WarningLetterProgressEnum.APPROVED,
    [latestWarningLetter]
  );

  const isIssueButtonDisabled = useMemo(
    () =>
      latestWarningLetter?.progress?.id === WarningLetterProgressEnum.APPROVED &&
      !latestWarningLetter?.intended_issuance_date,
    [latestWarningLetter]
  );

  const handleApprovalsButtonClick = useCallback(
    (isApprove: boolean) => {
      setOpen({
        content: (
          <ConfirmationModal
            title={`${isApprove ? "Approve" : "Reject"} Warning Letter?`}
            description={`You are about to ${isApprove ? "approve" : "reject"} this Warning Letter. ${
              !isApprove
                ? "This action will return the Warning Letter to the officer for further review and revision. "
                : ""
            }Are you sure?`}
            confirmButtonText={isApprove ? "Approve" : "Reject"}
            onConfirm={() => {
              updateWarningLetterApprovalStatus({
                inspectionWarningLetterId: latestWarningLetter.id ?? 0,
                approvalId: warningLetterApprovalsData?.[0]?.id ?? 0,
                statusPayload: {
                  approval_status: isApprove
                    ? APPROVAL_STATUS.APPROVED
                    : APPROVAL_STATUS.NOT_APPROVED,
                  approved_by_id: currentUserStaffId,
                },
              });
            }}
          />
        ),
      });
    },
    [
      currentUserStaffId,
      setOpen,
      updateWarningLetterApprovalStatus,
      latestWarningLetter.id,
      warningLetterApprovalsData,
    ]
  );

  const handleIssueButtonClick = useCallback(() => {
    setOpen({
      content: (
        <IssueEnforcementModal
          onSubmit={(message) => {
            refetchDataAndClose(message);
          }}
          warningLetter={latestWarningLetter}
        />
      ),
    });
  }, [setOpen, latestWarningLetter, refetchDataAndClose]);

  return (
    <>
      {isShowSendForApprovalButton && (
        <Button
          variant="text"
          onClick={handleSendForApproval}
          disabled={isDisableSendApprovalButton}
        >
          <SendRounded sx={{ mr: 1, fontSize: 20 }} />
          Send for Approval
        </Button>
      )}
      {isShowApprovalButtons && (
        <Box sx={{ display: "inline-flex", gap: 1 }}>
          <Button
            color="secondary"
            size="small"
            onClick={() => handleApprovalsButtonClick(true)}
          >
            Approve
          </Button>
          <Button
            color="secondary"
            size="small"
            onClick={() => handleApprovalsButtonClick(false)}
          >
            Not Approve
          </Button>
        </Box>
      )}
      {isShowIssueButton && (
        <Button
          onClick={handleIssueButtonClick}
          disabled={isIssueButtonDisabled}
        >
          Issue Warning Letter
        </Button>
      )}
    </>
  );
};

export default WarningLetterApprovalButtons;
