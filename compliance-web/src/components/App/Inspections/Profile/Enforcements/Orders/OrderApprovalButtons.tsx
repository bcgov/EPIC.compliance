import { useStaffUsersData } from "@/hooks/useStaff";
import { SendRounded } from "@mui/icons-material";
import { Box, Button } from "@mui/material";
import { SendForApprovalFormType } from "@/components/App/Inspections/Profile/SendForApprovalModal";
import { useCallback, useMemo } from "react";
import SendForApprovalModal from "@/components/App/Inspections/Profile/SendForApprovalModal";
import { notify } from "@/store/snackbarStore";
import { useModal } from "@/store/modalStore";
import {
  useCreateOrderApproval,
  useFetchOrderApprovals,
  useUpdateOrderApprovalStatus,
  useUpdateOrderStatus,
  useInspectionOrdersData,
} from "@/hooks/useInspectionOrders";
import { StaffUser } from "@/models/Staff";
import { OrderApproval } from "@/models/OrderApproval";
import { useCurrentLoggedInUser } from "@/hooks/useAuthorization";
import {
  APPROVAL_STATUS,
  OrderStatusEnum,
  STAFF_USER_POSITION,
} from "@/utils/constants";
import { OrderProgressEnum } from "@/utils/constants";
import { InspectionOrder } from "@/models/InspectionOrder";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import { useQueryClient } from "@tanstack/react-query";
import IssueEnforcementModal from "@/components/App/Inspections/Profile/Enforcements/IssueEnforcementModal";
import { useDrawer } from "@/store/drawerStore";
import OrderRecindModal from "./OrderRecindModal";
import { Inspection } from "@/models/Inspection";

const OrderApprovalButtons = ({
  inspectionOrder,
  inspection,
  caseFileId,
  openEnforcementOrderDrawer,
}: {
  inspectionOrder: InspectionOrder;
  inspection: Inspection;
  caseFileId: number;
  openEnforcementOrderDrawer?: (order: InspectionOrder) => void;
}) => {
  const { setOpen, setClose } = useModal();
  const { setClose: setDrawerClose } = useDrawer();
  const { data: staffData } = useStaffUsersData();
  const currentUser = useCurrentLoggedInUser();
  const queryClient = useQueryClient();

  // Get the latest order data from cache to ensure buttons update immediately
  const { data: ordersData } = useInspectionOrdersData(inspection.id);
  const latestOrder = useMemo(() => {
    return (
      ordersData?.find((order) => order.id === inspectionOrder.id) ||
      inspectionOrder
    );
  }, [ordersData, inspectionOrder]);

  const { data: orderApprovalsData } = useFetchOrderApprovals(
    latestOrder.id ?? 0
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
        queryKey: ["inspection-orders", inspection.id],
      });
      queryClient.invalidateQueries({
        queryKey: ["inspection-orders-projectwise", caseFileId],
      });
      setClose();
      setDrawerClose();
    },
    [queryClient, inspection, setClose, setDrawerClose, caseFileId]
  );

  const onSuccess = useCallback(
    (data: OrderApproval) => {
      queryClient.setQueryData(
        ["order-approvals", latestOrder.id],
        (oldData: OrderApproval[]) => {
          return [...oldData, data];
        }
      );
      refetchDataAndClose("Approval request sent");
    },
    [refetchDataAndClose, queryClient, latestOrder.id]
  );

  const { mutate: createOrderApproval, isPending } =
    useCreateOrderApproval(onSuccess);

  const onApprovalSuccess = useCallback(
    (data: OrderApproval) => {
      notify.success("Approval status updated");
      queryClient.setQueryData(
        ["order-approvals", latestOrder.id],
        (oldData: OrderApproval[]) => {
          return oldData.map((approval) =>
            approval.id === data.id ? data : approval
          );
        }
      );
      refetchDataAndClose("Approval status updated");
    },
    [latestOrder.id, queryClient, refetchDataAndClose]
  );

  const { mutate: updateOrderApprovalStatus } =
    useUpdateOrderApprovalStatus(onApprovalSuccess);

  const onSendForApprovalSubmitHandler = useCallback(
    (data: SendForApprovalFormType) => {
      const directorId = (data.director as StaffUser).id;
      createOrderApproval({
        inspectionOrderId: latestOrder.id ?? 0,
        approvalPayload: {
          approved_by_id: directorId,
        },
      });
    },
    [createOrderApproval, latestOrder.id]
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

  const { mutate: updateOrderStatus } =
    useUpdateOrderStatus(refetchDataAndClose);

  const isInDeputyReview = useMemo(
    () => latestOrder.order_progress?.id === OrderProgressEnum.DEPUTY_REVIEW,
    [latestOrder.order_progress]
  );

  const isInDrafting = useMemo(
    () => latestOrder.order_progress?.id === OrderProgressEnum.DRAFTING,
    [latestOrder.order_progress]
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
    () => latestOrder?.order_progress?.id === OrderProgressEnum.APPROVED,
    [latestOrder]
  );

  const isIssueButtonDisabled = useMemo(
    () =>
      latestOrder?.order_progress?.id === OrderProgressEnum.APPROVED &&
      !latestOrder?.intended_issuance_date,
    [latestOrder]
  );

  const isShowRescindCloseButton = useMemo(
    () =>
      latestOrder?.order_progress?.id === OrderProgressEnum.ISSUED &&
      latestOrder.order_status?.id === OrderStatusEnum.OPEN,
    [latestOrder]
  );

  const isShowReopenButton = useMemo(
    () =>
      latestOrder?.order_status?.id === OrderStatusEnum.CLOSED &&
      !isShowRescindCloseButton,
    [latestOrder, isShowRescindCloseButton]
  );

  const handleApprovalsButtonClick = useCallback(
    (isApprove: boolean) => {
      setOpen({
        content: (
          <ConfirmationModal
            title={`${isApprove ? "Approve" : "Reject"} Order?`}
            description={`You are about to ${isApprove ? "approve" : "reject"} this Order. ${
              !isApprove
                ? "This action will return the Order to the officer for further review and revision. "
                : ""
            }Are you sure?`}
            confirmButtonText={isApprove ? "Approve" : "Reject"}
            onConfirm={() => {
              updateOrderApprovalStatus({
                inspectionOrderId: latestOrder.id ?? 0,
                approvalId: orderApprovalsData?.[0]?.id ?? 0,
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
      updateOrderApprovalStatus,
      latestOrder.id,
      orderApprovalsData,
    ]
  );

  const handleIssueButtonClick = useCallback(() => {
    setOpen({
      content: (
        <IssueEnforcementModal
          onSubmit={(message) => {
            refetchDataAndClose(message);
          }}
          inspectionOrder={latestOrder}
        />
      ),
    });
  }, [setOpen, latestOrder, refetchDataAndClose]);

  const handleStatusButtonClick = useCallback(
    (status: OrderStatusEnum) => {
      let title, description, confirmButtonText: string | undefined;

      if (status === OrderStatusEnum.CLOSED) {
        title = "Close Order";
        description = `You are about to close this Order ${latestOrder.order_number}.
          Once closed, you can't inspect against it. In order to inspect, you need to reopen it again.
          Are you sure?`;
        confirmButtonText = "Close Order";
      } else if (status === OrderStatusEnum.OPEN) {
        title = "Reopen Order";
        description = `You are about to reopen Order ${latestOrder.order_number}. Once reopened, you can inspect against it. 
          Are you sure?`;
        confirmButtonText = "Reopen Order";
      }
      setOpen({
        content: (
          <ConfirmationModal
            title={title ?? ""}
            description={description ?? ""}
            confirmButtonText={confirmButtonText}
            onConfirm={() => {
              updateOrderStatus({
                inspectionOrderId: latestOrder.id ?? 0,
                statusPayload: {
                  status: status,
                },
              });
            }}
          />
        ),
      });
    },
    [setOpen, latestOrder.order_number, latestOrder.id, updateOrderStatus]
  );

  const handleRecindButtonClick = useCallback(() => {
    setOpen({
      content: (
        <OrderRecindModal
          order={latestOrder}
          onSuccess={(message, data) => {
            refetchDataAndClose(message);
            if (data) {
              openEnforcementOrderDrawer?.(data);
            }
          }}
          isHistoricalInspection={inspection.is_history}
        />
      ),
    });
  }, [
    setOpen,
    latestOrder,
    inspection,
    refetchDataAndClose,
    openEnforcementOrderDrawer,
  ]);

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
          Issue Order
        </Button>
      )}
      {isShowRescindCloseButton && (
        <Box sx={{ display: "inline-flex", gap: 2 }}>
          <Button color="secondary" onClick={handleRecindButtonClick}>
            Rescind Order
          </Button>
          <Button
            onClick={() => handleStatusButtonClick(OrderStatusEnum.CLOSED)}
          >
            Close Order
          </Button>
        </Box>
      )}
      {isShowReopenButton && (
        <Button
          color="secondary"
          onClick={() => handleStatusButtonClick(OrderStatusEnum.OPEN)}
        >
          Reopen
        </Button>
      )}
    </>
  );
};

export default OrderApprovalButtons;
