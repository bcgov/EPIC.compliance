import MenuActionDropdown from "@/components/Shared/MenuActionDropdown";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import {
  useDeleteInspection,
  useUpdateInspectionStatus,
  useInspectionByNumber,
} from "@/hooks/useInspections";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import { useModal } from "@/store/modalStore";
import { notify } from "@/store/snackbarStore";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import React, { useCallback } from "react";

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
    queryClient.removeQueries({
      queryKey: ["inspection", inspectionData?.ir_number],
    });
    router.navigate({ to: "/ce-database/inspections" });
  }, [router, setClose, queryClient, inspectionData]);

  const { mutate: updateInspectionInspection } = useUpdateInspectionStatus(
    onUpdateStatusSuccess
  );

  const { mutate: deleteInspection } = useDeleteInspection(onDeleteSuccess);

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
      hidden: ["canceled", "closed"].includes(status?.toLowerCase()),
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
      hidden: ["canceled", "closed"].includes(status?.toLowerCase()),
    },
    {
      text: "Close",
      onClick: () => {
        // Handle closing inspection
        setOpen({
          content: (
            <ConfirmationModal
              title="Close Inspection?"
              description="Are you sure you want to close inspection?"
              confirmButtonText="Close Inspection"
              onConfirm={() => {
                updateInspectionInspection({
                  id: inspectionData?.id ?? 0,
                  inspectionStatus: { status: "CLOSED" },
                });
              }}
            />
          ),
          width: "420px",
        });
      },
      hidden: ["canceled", "closed"].includes(status?.toLowerCase()),
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
      hidden: ["canceled", "open"].includes(status?.toLowerCase()),
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
