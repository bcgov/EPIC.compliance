import { KC_USER_GROUPS, useIsRolesAllowed } from "@/hooks/useAuthorization";
import { useInspectionByNumber } from "@/hooks/useInspections";
import { useDrawer } from "@/store/drawerStore";
import { notify } from "@/store/snackbarStore";
import { Box } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute, useParams } from "@tanstack/react-router";
import React, { useCallback, useEffect, useMemo } from "react";
import ContinuationReport from "@/components/App/ContinuationReports/ContinuationReport";
import FileProfileHeader from "@/components/App/FileProfileHeader";
import InspectionDrawer from "@/components/App/Inspections/InspectionDrawer";
import InspectionGeneralInformation from "@/components/App/Inspections/Profile/InspectionGeneralInformation";
import InspectionReports from "@/components/App/Inspections/Profile/InspectionReports";
import InspectionRequirements from "@/components/App/Inspections/Profile/InspectionRequirements";
import ErrorPage from "@/components/Shared/ErrorPage";
import LoadingPage from "@/components/Shared/LoadingPage";
import TabPanel from "@/components/Shared/TabPanel";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import { CaseFile } from "@/models/CaseFile";
import { useTab } from "@/store/tabStore";
import { MQ } from "@/styles/responsive";
import {
  CR_CONTEXT_TYPE,
  DRAWER_WIDTHS,
  FILE_PROFILE_CONTEXT,
} from "@/utils/constants";
import InspectionEnforcements from "@/components/App/Inspections/Profile/InspectionEnforcements";
import useResponsiveDrawerWidth from "@/hooks/useResponsiveDrawerWidth";

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
  const { currentTab, resetTab } = useTab();

  useEffect(() => {
    if (inspectionNumber) {
      resetTab();
    }
  }, [resetTab, inspectionNumber]);

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

  const isUserEditAllowed = useIsRolesAllowed(
    [KC_USER_GROUPS.SUPERUSER],
    inspectionData?.primary_officer ? [inspectionData?.primary_officer] : []
  );

  const showCreateCREntryButton =
    useIsRolesAllowed(
      [KC_USER_GROUPS.SUPERUSER],
      inspectionData?.primary_officer ? [inspectionData?.primary_officer] : []
    ) && caseFileData?.case_file_status === "Open";

  const isInspectionEditable = useMemo(() => {
    return (
      isUserEditAllowed && inspectionData?.inspection_status?.toLowerCase() === "open"
    );
  }, [inspectionData, isUserEditAllowed]);

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

  const drawerWidth = useResponsiveDrawerWidth(
    DRAWER_WIDTHS.INSPECTION_DRAWER,
    { mdToLgMax: "715px" }
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
      width: drawerWidth,
    });
  }, [setOpen, handleOnSubmit, inspectionData, caseFileData, drawerWidth]);

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
        profileContext={FILE_PROFILE_CONTEXT.INSPECTION}
        caseFileNumber={caseFileData?.case_file_number}
        isHistorical={inspectionData.is_history}
      />
      <Box
        p="1rem 1rem 1.25rem 3.75rem"
        display="flex"
        gap={3}
        sx={{
          flexDirection: "row",
          [MQ.mdToLg]: {
            flexDirection: "column",
          },
        }}
      >
        <>
          <TabPanel value={currentTab} index={0} id="inspection-profile">
            <InspectionGeneralInformation
              inspectionData={inspectionData}
              caseFileData={caseFileData as CaseFile}
              onEdit={handleOpenEditModal}
              allowEdit={isInspectionEditable}
            />
          </TabPanel>
          <TabPanel value={currentTab} index={1} id="inspection-requirements">
            <InspectionRequirements inspectionData={inspectionData} />
          </TabPanel>
          <TabPanel value={currentTab} index={2} id="inspection-enforcement">
            <InspectionEnforcements inspectionData={inspectionData} />
          </TabPanel>
          <TabPanel value={currentTab} index={3} id="inspection-report">
            <InspectionReports inspectionData={inspectionData} />
          </TabPanel>
        </>
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
