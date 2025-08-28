import MenuActionDropdown from "@/components/Shared/MenuActionDropdown";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import {
  useDeleteComplaint,
  useUpdateComplaintStatus,
} from "@/hooks/useComplaints";
import { Complaint } from "@/models/Complaint";
import { useModal } from "@/store/modalStore";
import { notify } from "@/store/snackbarStore";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import React, { useCallback } from "react";

interface ComplaintFileActionsProps {
  status: string;
  fileNumber: string;
}

const ComplaintFileActions: React.FC<ComplaintFileActionsProps> = ({
  status,
  fileNumber,
}) => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { setOpen, setClose } = useModal();

  const complaintData = queryClient.getQueryData<Complaint>([
    "complaint",
    fileNumber,
  ]);

  const { data: caseFileData } = useCaseFileByNumber(
    complaintData?.case_file?.case_file_number || ""
  );

  const isCaseFileClosed = caseFileData?.case_file_status?.toLowerCase() === "closed" ||
    complaintData?.case_file?.case_file_status?.toLowerCase() === "closed";

  const onUpdateStatusSuccess = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: ["complaint", fileNumber],
    });
    queryClient.invalidateQueries({
      queryKey: ["continuation-reports", complaintData?.case_file_id],
    });
    notify.success("Complaint status updated");
    setClose();
  }, [complaintData, fileNumber, queryClient, setClose]);

  const onDeleteSuccess = useCallback(() => {
    notify.success("Complaint deleted!");
    setClose();
    queryClient.removeQueries({
      queryKey: ["complaint", complaintData?.complaint_number],
    });
    router.navigate({ to: "/ce-database/complaints" });
  }, [router, setClose, queryClient, complaintData]);

  const { mutate: updateComplaintStatus } = useUpdateComplaintStatus(
    onUpdateStatusSuccess
  );

  const { mutate: deleteComplaint } = useDeleteComplaint(onDeleteSuccess);

  const actionsList = [
    {
      text: "Close Complaint",
      onClick: () => {
        // Handle closing complaint
        setOpen({
          content: (
            <ConfirmationModal
              title="Close Complaint?"
              description="Are you sure you want to close this complaint? This action cannot be undone without reopening the complaint."
              confirmButtonText="Close Complaint"
              onConfirm={() => {
                updateComplaintStatus({
                  id: complaintData?.id ?? 0,
                  complaintStatus: { status: "CLOSED" },
                });
              }}
            />
          ),
        });
      },
      hidden: status?.toLowerCase() === "closed",
    },
    {
      text: "Reopen Complaint",
      onClick: () => {
        // Handle reopening complaint
        setOpen({
          content: (
            <ConfirmationModal
              title="Reopen Complaint?"
              description="Are you sure you want to reopen this complaint?"
              confirmButtonText="Reopen Complaint"
              onConfirm={() => {
                updateComplaintStatus({
                  id: complaintData?.id ?? 0,
                  complaintStatus: { status: "OPEN" },
                });
              }}
            />
          ),
        });
      },
      hidden: status?.toLowerCase() === "open",
    },
    {
      text: "Delete Complaint",
      onClick: () => {
        // Handle deleting complaint
        setOpen({
          content: (
            <ConfirmationModal
              title="Delete Complaint?"
              description="You are about to delete this complaint. Are you sure?"
              confirmButtonText="Delete"
              onConfirm={() => {
                deleteComplaint(complaintData?.id ?? 0);
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

export default ComplaintFileActions;
