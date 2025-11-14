import MenuActionDropdown from "@/components/Shared/MenuActionDropdown";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import {
  useDeleteInspection,
  useUpdateInspectionStatus,
  useInspectionByNumber,
  useCheckPendingItems,
} from "@/hooks/useInspections";
import { PendingItem } from "@/models/Inspection";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import InspectionPendingEnforcementsDescription from "./InspectionPendingEnforcementsDescription";
import { useModal } from "@/store/modalStore";
import { notify } from "@/store/snackbarStore";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import React, { useCallback } from "react";
import { InspectionStatusEnum } from "@/utils/constants";

interface InspectionFileActionsProps {
  status: string;
  fileNumber: string;
}

const InspectionFileActions: React.FC<InspectionFileActionsProps> = ({
  status,
  fileNumber,
}) => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { setOpen, setClose } = useModal();

  const { data: inspectionData } = useInspectionByNumber(fileNumber);
  
  const { data: caseFileData } = useCaseFileByNumber(
    inspectionData?.case_file?.case_file_number || ""
  );

  
  const isCaseFileClosed = caseFileData?.case_file_status?.toLowerCase() === "closed" || 
                          inspectionData?.case_file?.case_file_status?.toLowerCase() === "closed";

  const onUpdateStatusSuccess = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: ["inspection", fileNumber],
    });
    queryClient.invalidateQueries({
      queryKey: ["continuation-reports", inspectionData?.case_file_id],
    });
    queryClient.invalidateQueries({
      queryKey: ["inspection-requirements", inspectionData?.id],
    });
  
 
    notify.success("Inspection status updated");
    setClose();
  }, [fileNumber, inspectionData, queryClient, setClose]);

  const onDeleteSuccess = useCallback(() => {
    notify.success("Inspection deleted!");
    setClose();
    // Navigate away first to unmount the component
    router.navigate({ to: `/ce-database/case-files/${inspectionData?.case_file?.case_file_number}` });
    // Delay query cleanup to ensure navigation completes first
    setTimeout(() => {
      queryClient.removeQueries({
        queryKey: ["inspection", inspectionData?.ir_number],
      });
    }, 100);
  }, [router, setClose, queryClient, inspectionData]);

  const { mutate: updateInspectionInspection } = useUpdateInspectionStatus(
    onUpdateStatusSuccess
  );

  const { mutate: deleteInspection } = useDeleteInspection(onDeleteSuccess);

  // Use the hook for checking pending items on demand
  const checkPendingItemsMutation = useCheckPendingItems();

  // Handle the pending items check result
  const handlePendingItemsResult = useCallback((pendingItems: PendingItem[]) => {
    const hasPendingItems = pendingItems.length > 0 && 
      pendingItems.some((item: PendingItem) => !item.is_created);
    const hasUnissuedItems = pendingItems.length > 0 && 
      pendingItems.some((item: PendingItem) => !item.is_issued);

    setOpen({
      content: (
        <ConfirmationModal
          title={
            hasPendingItems || hasUnissuedItems
              ? "Cannot Close Inspection"
              : "Close Inspection?"
          }
          formattedDescription={
            hasPendingItems || hasUnissuedItems ? (
              <InspectionPendingEnforcementsDescription
                pendingEnforcements={pendingItems}
              />
            ) : (
              "Are you sure you want to close inspection?"
            )
          }
          confirmButtonText={
            hasPendingItems || hasUnissuedItems
              ? "Return to Inspection"
              : "Close Inspection"
          }
          onConfirm={() => {
            if (hasPendingItems || hasUnissuedItems) {
              setClose();
              return;
            }
            updateInspectionInspection({
              id: inspectionData?.id ?? 0,
              inspectionStatus: { status: "CLOSED" },
            });
          }}
        />
      ),
      width: "420px",
    });
  }, [setOpen, setClose, updateInspectionInspection, inspectionData?.id]);

  const actionsList = [
    {
      text: "Cancel Inspection",
      onClick: () => {
        // Handle canceling inspection
        setOpen({
          content: (
            <ConfirmationModal
              title="Cancel Inspection?"
              description="Are you sure you want to cancel this inspection?"
              confirmButtonText="Cancel Inspection"
              onConfirm={() => {
                updateInspectionInspection({
                  id: inspectionData?.id ?? 0,
                  inspectionStatus: { status: "CANCELED" },
                });
              }}
            />
          ),
        });
      },
      hidden: [InspectionStatusEnum.CANCELED.toLowerCase(), InspectionStatusEnum.CLOSED.toLowerCase(), InspectionStatusEnum.CLOSE_AS_NOTE.toLowerCase()].includes(status?.toLowerCase()),
    },
    {
      text: "Close as Note to File",
      onClick: () => {
        // Handle closing inspection
        setOpen({
          content: (
            <ConfirmationModal
              title="Close Inspection as Note to File?"
              description="Are you sure you want to close inspection as note to file?"
              confirmButtonText="Close Inspection"
              onConfirm={() => {
                updateInspectionInspection({
                  id: inspectionData?.id ?? 0,
                  inspectionStatus: {
                    status: "CLOSE_AS_NOTE",
                  },
                });
              }}
            />
          ),
          width: "420px",
        });
      },
      hidden: [InspectionStatusEnum.CANCELED.toLowerCase(), InspectionStatusEnum.CLOSED.toLowerCase(), InspectionStatusEnum.CLOSE_AS_NOTE.toLowerCase()].includes(status?.toLowerCase()),
    },
    {
      text: "Close",
      onClick: () => {
        if (inspectionData?.id) {
          // Show loading modal while checking pending items
          if (checkPendingItemsMutation.isPending) {
            return; // Already checking
          }

          setOpen({
            content: (
              <ConfirmationModal
                title="Checking Pending Items..."
                description="Please wait while we check for pending items..."
                showActions={false}
                onConfirm={() => {}} // Disabled while loading
              />
            ),
          });

          // Trigger the mutation to fetch pending items
          checkPendingItemsMutation.mutate(inspectionData.id, {
            onSuccess: handlePendingItemsResult,
            onError: () => {
              notify.error("Failed to check pending items. Please try again.");
            },
          });
        }
      },
      hidden: [InspectionStatusEnum.CANCELED.toLowerCase(), InspectionStatusEnum.CLOSED.toLowerCase(), InspectionStatusEnum.CLOSE_AS_NOTE.toLowerCase()].includes(status?.toLowerCase()),
    },
    {
      text: "Reopen Inspection",
      onClick: () => {
        // Handle reopening inspection
        setOpen({
          content: (
            <ConfirmationModal
              title="Reopen Inspection?"
              description="You are about to reopen this inspection. Are you sure?"
              confirmButtonText="Reopen"
              onConfirm={() => {
                updateInspectionInspection({
                  id: inspectionData?.id ?? 0,
                  inspectionStatus: { status: "OPEN" },
                });
              }}
            />
          ),
        });
      },
      hidden: [InspectionStatusEnum.CANCELED.toLowerCase(), InspectionStatusEnum.OPEN.toLowerCase()].includes(status?.toLowerCase()),
    },
    {
      text: "Delete Inspection",
      onClick: () => {
        // Handle deleting inspection
        setOpen({
          content: (
            <ConfirmationModal
              title="Delete Inspection?"
              description="You are about to delete this inspection. Are you sure?"
              confirmButtonText="Delete"
              onConfirm={() => {
                deleteInspection(inspectionData?.id ?? 0);
              }}
            />
          ),
        });
      },
      hidden: false,
    },
  ];

  
  if (isCaseFileClosed) {
    return <></>;
  }

  return <MenuActionDropdown actions={actionsList} />;
};

export default InspectionFileActions;
