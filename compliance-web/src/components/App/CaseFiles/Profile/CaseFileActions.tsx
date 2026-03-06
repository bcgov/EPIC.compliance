import LinkCaseFileModal from "@/components/App/CaseFiles/Profile/LinkCaseFileModal";
import CaseFileOpenItemsDescription from "@/components/App/CaseFiles/Profile/CaseFileOpenItemsDescription";
import MenuActionDropdown from "@/components/Shared/MenuActionDropdown";
import ConfirmationModal from "@/components/Shared/Popups/ConfirmationModal";
import {
  useCaseFileOpenItems,
  useDeleteCaseFile,
  useLinkCaseFile,
  useUnlinkCaseFile,
  useUpdateCaseFileStatus,
} from "@/hooks/useCaseFiles";
import { CaseFile, CaseFileLink } from "@/models/CaseFile";
import { useModal } from "@/store/modalStore";
import { notify } from "@/store/snackbarStore";
import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "@tanstack/react-router";
import React, { useCallback } from "react";
import { useAuth } from "react-oidc-context";
import { KC_USER_GROUPS, useIsRolesAllowed } from "@/hooks/useAuthorization";
import { CaseFileStatusEnum } from "@/utils/constants";
import { useInspectionsMoreDetailsByCaseFileId } from "@/hooks/useInspections";

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
  const { user } = useAuth();
  const isSuperUser = useIsRolesAllowed([KC_USER_GROUPS.SUPERUSER]);

  const caseFileData = queryClient.getQueryData<CaseFile>([
    "case-file",
    fileNumber,
  ]);

  const { data: caseFileOpenItems } = useCaseFileOpenItems(
    caseFileData?.id ?? 0
  );

  const { data: detailedInspections} = useInspectionsMoreDetailsByCaseFileId(caseFileData?.id);

  const isPrimaryOfficer =
    caseFileData?.primary_officer?.auth_user_guid ===
    user?.profile?.preferred_username;

  const otherAssignedOfficers =
    caseFileData?.officers?.map((o) => o?.auth_user_guid) ?? [];

  const canLinkOrUnlinkCaseFile =
    isSuperUser ||
    isPrimaryOfficer ||
    otherAssignedOfficers.includes(user?.profile?.preferred_username ?? "");

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

  const onLinkCaseFileSuccess = useCallback((response: CaseFileLink) => {
    notify.success("Case file link is updated");
    closeAndRefresh();
    queryClient.invalidateQueries({
      queryKey: ["case-file", response?.target?.case_file_number],
    });
  }, [closeAndRefresh, queryClient]);

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

  const onOpenItemClick = useCallback(
    (url: string, params: { [key: string]: string }) => {
      router.navigate({
        to: url,
        params: params,
      });
      setClose();
    },
    [router, setClose]
  );

  const closeCaseFile = useCallback(() => {
    setOpen({
      content: (
        <ConfirmationModal
          title={
            caseFileOpenItems?.has_open_items
              ? "Cannot Close Case File"
              : "Close Case File?"
          }
          formattedDescription={
            <CaseFileOpenItemsDescription
              caseFileOpenItems={caseFileOpenItems}
              onOpenItemClick={onOpenItemClick}
            />
          }
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
    onOpenItemClick,
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
      hidden:
        status === CaseFileStatusEnum.CLOSED || !canLinkOrUnlinkCaseFile,
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
      hidden:
        status === CaseFileStatusEnum.CLOSED || !canLinkOrUnlinkCaseFile,
    },
    {
      text: "Close Case File",
      onClick: closeCaseFile,
      hidden: status === CaseFileStatusEnum.CLOSED,
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
                queryClient.invalidateQueries({
                  queryKey: ["case-file", caseFileData?.case_file_number],
                });
                detailedInspections?.map((inspection) => {
                  queryClient.invalidateQueries({
                    queryKey: ["inspection", inspection.ir_number],
                  });
                });
              }}
            />
          ),
        });
      },
      hidden: status === CaseFileStatusEnum.OPEN,
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
