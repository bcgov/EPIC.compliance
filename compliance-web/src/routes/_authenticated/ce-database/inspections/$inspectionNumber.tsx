import React, { useCallback } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute, useParams } from "@tanstack/react-router";
import { Box } from "@mui/material";
import { useInspectionByNumber } from "@/hooks/useInspections";
import { useDrawer } from "@/store/drawerStore";
import { useIsRolesAllowed, KC_USER_GROUPS } from "@/hooks/useAuthorization";
import { notify } from "@/store/snackbarStore";

import InspectionDrawer from "@/components/App/Inspections/InspectionDrawer";
import FileProfileHeader from "@/components/App/FileProfileHeader";
import ContinuationReport from "@/components/App/ContinuationReports/ContinuationReport";
import InspectionGeneralInformation from "@/components/App/Inspections/Profile/InspectionGeneralInformation";
import ErrorPage from "@/components/Shared/ErrorPage";
import LoadingPage from "@/components/Shared/LoadingPage";
import { CR_CONTEXT_TYPE } from "@/utils/constants";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import { CaseFile } from "@/models/CaseFile";

export const Route = createFileRoute(
  "/_authenticated/ce-database/inspections/$inspectionNumber"
)({
  component: React.memo(InspectionProfilePage),
  notFoundComponent: () => <p>Inspection not found!</p>,
});

function InspectionProfilePage() {
  const queryClient = useQueryClient();
  const { inspectionNumber } = useParams({ strict: false });
  const { setOpen, setClose } = useDrawer();

  const {
    status,
    data: inspectionData,
    isError,
    error,
    isLoading,
  } = useInspectionByNumber(inspectionNumber!);

  const { data: caseFileData } = useCaseFileByNumber(
    inspectionData?.case_file.case_file_number ?? ""
  );

  const showEditInspectionButton = useIsRolesAllowed(
    [KC_USER_GROUPS.SUPERUSER],
    inspectionData?.primary_officer ? [inspectionData?.primary_officer] : []
  );

  const showCreateCREntryButton = useIsRolesAllowed(
    [KC_USER_GROUPS.SUPERUSER],
    inspectionData?.primary_officer ? [inspectionData?.primary_officer] : []
  );

  // Event handlers
  const handleOnSubmit = useCallback(
    (submitMsg: string) => {
      queryClient.invalidateQueries({
        queryKey: ["inspection", inspectionNumber],
      });
      setClose();
      notify.success(submitMsg);
    },
    [queryClient, inspectionNumber, setClose]
  );

  const handleOpenEditModal = useCallback(() => {
    setOpen({
      content: (
        <InspectionDrawer
          onSubmit={handleOnSubmit}
          inspection={inspectionData}
          caseFile={caseFileData as CaseFile}
        />
      ),
      width: "1118px",
    });
  }, [setOpen, handleOnSubmit, inspectionData, caseFileData]);

  // Conditional rendering
  if (isError) {
    return <ErrorPage error={error} />;
  }

  if (!inspectionNumber || status === "pending") {
    return <LoadingPage isLoading={isLoading} />;
  }

  return (
    <>
      <FileProfileHeader
        fileNumber={inspectionNumber}
        status={inspectionData.inspection_status}
        breadcrumbs={[
          { label: "Inspections", to: "/ce-database/inspections" },
          { label: inspectionNumber },
        ]}
      />
      <Box p="1rem 1rem 1.25rem 3.75rem" display="flex" gap={3}>
        <InspectionGeneralInformation
          inspectionData={inspectionData}
          onEdit={handleOpenEditModal}
          allowEdit={showEditInspectionButton}
        />
        <ContinuationReport
          caseFileId={inspectionData.case_file_id}
          contextType={CR_CONTEXT_TYPE.INSPECTION}
          contextId={inspectionData.id}
          allowCreateEntry={showCreateCREntryButton}
        />
      </Box>
    </>
  );
}
