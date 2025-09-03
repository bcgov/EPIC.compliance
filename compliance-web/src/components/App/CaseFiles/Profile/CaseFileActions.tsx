import LinkCaseFileModal from "@/components/App/CaseFiles/Profile/LinkCaseFileModal";
import MenuActionDropdown from "@/components/Shared/MenuActionDropdown";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import {
  useCaseFileOpenItems,
  useDeleteCaseFile,
  useLinkCaseFile,
  useUnlinkCaseFile,
  useUpdateCaseFileStatus,
} from "@/hooks/useCaseFiles";
import { CaseFile } from "@/models/CaseFile";
import { useModal } from "@/store/modalStore";
import { notify } from "@/store/snackbarStore";
import { Box, Typography } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import React, { useCallback } from "react";

interface CaseFileActionsProps {
  status: string;
  fileNumber: string;
}

const CaseFileActions: React.FC<CaseFileActionsProps> = ({
  status,
  fileNumber,
}) => {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { setOpen, setClose } = useModal();

  const caseFileData = queryClient.getQueryData<CaseFile>([
    "case-file",
    fileNumber,
  ]);

  const { data: caseFileOpenItems } = useCaseFileOpenItems(
    caseFileData?.id ?? 0
  );

  const closeAndRefresh = useCallback(() => {
    queryClient.invalidateQueries({
      queryKey: ["case-file", fileNumber],
    });
    queryClient.invalidateQueries({
      queryKey: ["continuation-reports", caseFileData?.id],
    });
    setClose();
  }, [caseFileData, fileNumber, queryClient, setClose]);

  const onUpdateStatusSuccess = useCallback(() => {
    notify.success("Case File status updated!");
    closeAndRefresh();
  }, [closeAndRefresh]);

  const onLinkCaseFileSuccess = useCallback(() => {
    notify.success("Case file link is updated");
    closeAndRefresh();
  }, [closeAndRefresh]);

  const onDeleteSuccess = useCallback(() => {
    notify.success("Case File deleted!");
    setClose();
    queryClient.removeQueries({
      queryKey: ["case-file", caseFileData?.case_file_number],
    });
    router.navigate({ to: "/ce-database/case-files" });
  }, [setClose, router, queryClient, caseFileData]);

  const { mutate: linkCaseFile } = useLinkCaseFile(onLinkCaseFileSuccess);
  const { mutate: unlinkCaseFile } = useUnlinkCaseFile(onLinkCaseFileSuccess);
  const { mutate: updateCaseFileStatus } = useUpdateCaseFileStatus(
    onUpdateStatusSuccess
  );
  const { mutate: deleteCaseFile } = useDeleteCaseFile(onDeleteSuccess);

  const closeCaseFile = useCallback(() => {
    const formattedDescription = caseFileOpenItems?.has_open_items ? (
      <Box sx={{ overflow: "auto", maxHeight: "570px" }}>
        <Typography variant="body1" mb={2}>
          This case file contains open items that must be closed before
          proceeding:
        </Typography>
        {caseFileOpenItems?.inspections.length > 0 && (
          <Box>
            <strong>Inspections:</strong>
            <ul>
              {caseFileOpenItems.inspections.map((inspection, index) => (
                <li key={index}>{inspection.number}</li>
              ))}
            </ul>
          </Box>
        )}
        {caseFileOpenItems?.complaints.length > 0 && (
          <Box>
            <strong>Complaints:</strong>
            <ul>
              {caseFileOpenItems.complaints.map((complaint, index) => (
                <li key={index}>{complaint.number}</li>
              ))}
            </ul>
          </Box>
        )}
        {caseFileOpenItems?.orders.length > 0 && (
          <Box>
            <strong>Orders:</strong>
            <ul>
              {caseFileOpenItems.orders.map((order, index) => (
                <li key={index}>{order.number}</li>
              ))}
            </ul>
          </Box>
        )}
        {caseFileOpenItems?.warning_letters.length > 0 && (
          <Box>
            <strong>Warning Letters:</strong>
            <ul>
              {caseFileOpenItems.warning_letters.map((warningLetter, index) => (
                <li key={index}>{warningLetter.number}</li>
              ))}
            </ul>
          </Box>
        )}
        {caseFileOpenItems?.violation_tickets.length > 0 && (
          <Box>
            <strong>Violation Tickets:</strong>
            <ul>
              {caseFileOpenItems.violation_tickets.map(
                (violationTicket, index) => (
                  <li key={index}>{violationTicket.number}</li>
                )
              )}
            </ul>
          </Box>
        )}
        {caseFileOpenItems?.administrative_penalties.length > 0 && (
          <Box>
            <strong>Administrative Penalties:</strong>
            <ul>
              {caseFileOpenItems.administrative_penalties.map(
                (administrativePenalty, index) => (
                  <li key={index}>{administrativePenalty.number}</li>
                )
              )}
            </ul>
          </Box>
        )}
        {caseFileOpenItems?.charge_recommendations.length > 0 && (
          <Box>
            <strong>Charge Recommendations:</strong>
            <ul>
              {caseFileOpenItems.charge_recommendations.map(
                (chargeRecommendation, index) => (
                  <li key={index}>{chargeRecommendation.number}</li>
                )
              )}
            </ul>
          </Box>
        )}
        {caseFileOpenItems?.restorative_justice.length > 0 && (
          <Box>
            <strong>Restorative Justice:</strong>
            <ul>
              {caseFileOpenItems.restorative_justice.map(
                (restorativeJustice, index) => (
                  <li key={index}>{restorativeJustice.number}</li>
                )
              )}
            </ul>
          </Box>
        )}
        <Typography variant="body1" pt={1}>
          Please close these items and try again.
        </Typography>
      </Box>
    ) : (
      <div>
        Are you sure you want to close this case file? This action cannot be
        undone without reopening the case file.
      </div>
    );
    setOpen({
      content: (
        <ConfirmationModal
          title={
            caseFileOpenItems?.has_open_items
              ? "Cannot Close Case File"
              : "Close Case File?"
          }
          formattedDescription={formattedDescription}
          confirmButtonText={
            caseFileOpenItems?.has_open_items
              ? "Return to Case File"
              : "Close Case File"
          }
          onConfirm={() => {
            if (caseFileOpenItems?.has_open_items) {
              setClose();
              return;
            }
            updateCaseFileStatus({
              id: caseFileData?.id ?? 0,
              caseFileStatus: { status: "CLOSED" },
            });
          }}
        />
      ),
    });
  }, [
    caseFileData,
    caseFileOpenItems,
    setClose,
    setOpen,
    updateCaseFileStatus,
  ]);

  const actionsList = [
    {
      text: "Link to Case File",
      onClick: () => {
        // Handle linking case file
        setOpen({
          content: (
            <LinkCaseFileModal
              fileNumber={fileNumber}
              linkedCaseFiles={caseFileData?.caseFileLinks ?? []}
              onSubmit={(caseFileId) => {
                linkCaseFile({ id: caseFileData?.id ?? 0, linkId: caseFileId });
              }}
            />
          ),
        });
      },
      hidden: status?.toLowerCase() === "closed",
    },
    {
      text: "Unlink from Case File",
      onClick: () => {
        // Handle unlinking case file
        setOpen({
          content: (
            <LinkCaseFileModal
              fileNumber={fileNumber}
              onSubmit={(caseFileId) => {
                unlinkCaseFile({
                  id: caseFileData?.id ?? 0,
                  linkId: caseFileId,
                });
              }}
              linkedCaseFiles={caseFileData?.caseFileLinks ?? []}
              isEdit
            />
          ),
        });
      },
      hidden: status?.toLowerCase() === "closed",
    },
    {
      text: "Close Case File",
      onClick: closeCaseFile,
      hidden: status?.toLowerCase() === "closed",
    },
    {
      text: "Reopen Case File",
      onClick: () => {
        // Handle reopening case file
        setOpen({
          content: (
            <ConfirmationModal
              title="Reopen Case File?"
              description="You are about to reopen this case file. Are you sure?"
              confirmButtonText="Reopen Case File"
              onConfirm={() => {
                updateCaseFileStatus({
                  id: caseFileData?.id ?? 0,
                  caseFileStatus: { status: "OPEN" },
                });
              }}
            />
          ),
        });
      },
      hidden: status?.toLowerCase() === "open",
    },
    {
      text: "Delete Case File",
      onClick: () => {
        // Handle deleting case file
        setOpen({
          content: (
            <ConfirmationModal
              title="Delete Case File?"
              description="You are about to delete this case file. Are you sure?"
              confirmButtonText="Delete"
              onConfirm={() => deleteCaseFile(caseFileData?.id ?? 0)}
            />
          ),
        });
      },
      hidden: false,
    },
  ];

  return <MenuActionDropdown actions={actionsList} />;
};

export default CaseFileActions;
