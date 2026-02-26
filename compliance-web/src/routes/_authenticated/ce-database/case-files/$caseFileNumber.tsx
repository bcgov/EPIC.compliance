import CaseFileDrawer from "@/components/App/CaseFiles/CaseFileDrawer";
import CaseFileGeneralInformation from "@/components/App/CaseFiles/Profile/CaseFileGeneralInformation";
import ContinuationReport from "@/components/App/ContinuationReports/ContinuationReport";
import FileProfileHeader from "@/components/App/FileProfileHeader";
import ErrorPage from "@/components/Shared/ErrorPage";
import LoadingPage from "@/components/Shared/LoadingPage";
import { KC_USER_GROUPS, useIsRolesAllowed } from "@/hooks/useAuthorization";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import { useDrawer } from "@/store/drawerStore";
import { notify } from "@/store/snackbarStore";
import { MQ } from "@/styles/responsive";
import {
  CR_CONTEXT_TYPE,
  DRAWER_WIDTHS,
  FILE_PROFILE_CONTEXT,
  INITIATION,
} from "@/utils/constants";
import { Box, useMediaQuery } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import React, { useCallback, useMemo } from "react";

export const Route = createFileRoute(
  "/_authenticated/ce-database/case-files/$caseFileNumber"
)({
  component: React.memo(CaseFileProfilePage),
  notFoundComponent: () => <p>Case File not found!</p>,
});

function CaseFileProfilePage() {
  const queryClient = useQueryClient();
  const { caseFileNumber } = Route.useParams();
  const { setOpen, setClose } = useDrawer();
  const isMdToLg = useMediaQuery(MQ.mdToLg);
  

  const {
    status,
    data: caseFileData,
    isError,
    error,
    isLoading,
  } = useCaseFileByNumber(caseFileNumber!);

  const isUserEditAllowed = useIsRolesAllowed(
    [KC_USER_GROUPS.SUPERUSER],
    caseFileData?.primary_officer ? [caseFileData.primary_officer] : []
  );
  const showCreateCREntryButton =
    useIsRolesAllowed(
      [KC_USER_GROUPS.SUPERUSER],
      caseFileData
        ? [...[caseFileData.primary_officer], ...caseFileData.officers]
        : []
    ) && caseFileData?.case_file_status === "Open";

  const isCaseFileEditable = useMemo(() => {
    return (
      isUserEditAllowed &&
      caseFileData?.case_file_status?.toLowerCase() === "open"
    );
  }, [caseFileData, isUserEditAllowed]);

  // Handlers
  const handleOnSubmit = useCallback(
    (submitMsg: string) => {
      queryClient.invalidateQueries({
        queryKey: ["case-file", caseFileNumber],
      });
      setClose();
      notify.success(submitMsg);
    },
    [queryClient, caseFileNumber, setClose]
  );

  const handleOpenEditModal = useCallback(() => {
    setOpen({
      content: (
        <CaseFileDrawer onSubmit={handleOnSubmit} caseFile={caseFileData} />
      ),
      width: DRAWER_WIDTHS.CASEFILE_DRAWER,
    });
  }, [caseFileData, handleOnSubmit, setOpen]);

  // Error Handling
  if (isError) {
    return <ErrorPage error={error} />;
  }

  // Loading State
  if (!caseFileNumber || status === "pending") {
    return <LoadingPage isLoading={isLoading} />;
  }

  return (
    <>
      <FileProfileHeader
        fileNumber={caseFileNumber}
        status={caseFileData.case_file_status}
        breadcrumbs={[
          { label: "Case Files", to: "/ce-database/case-files" },
          { label: caseFileNumber },
        ]}
        profileContext={FILE_PROFILE_CONTEXT.CASEFILE}
        isInititationOther={caseFileData.initiation.id === INITIATION.OTHER_ID}
      />
      <Box p="1rem 1rem 1.25rem 3.75rem" display="flex" gap={3} sx={{
        flexDirection: isMdToLg ? "column": "row",
      }}>
        <CaseFileGeneralInformation
          caseFileData={caseFileData}
          onEdit={handleOpenEditModal}
          allowEdit={isCaseFileEditable}
        />
        <ContinuationReport
          caseFileId={caseFileData.id}
          contextType={CR_CONTEXT_TYPE.CASEFILE}
          contextId={caseFileData.id}
          allowCreateEntry={showCreateCREntryButton}
        />
      </Box>
    </>
  );
}
