import ComplaintDrawer from "@/components/App/Complaints/ComplaintDrawer";
import ComplaintGeneralInformation from "@/components/App/Complaints/Profile/ComplaintGeneralInformation";
import ContinuationReport from "@/components/App/ContinuationReports/ContinuationReport";
import FileProfileHeader from "@/components/App/FileProfileHeader";
import ErrorPage from "@/components/Shared/ErrorPage";
import LoadingPage from "@/components/Shared/LoadingPage";
import { KC_USER_GROUPS, useIsRolesAllowed } from "@/hooks/useAuthorization";
import { useCaseFileByNumber } from "@/hooks/useCaseFiles";
import { useComplaintByNumber } from "@/hooks/useComplaints";
import { CaseFile } from "@/models/CaseFile";
import { useDrawer } from "@/store/drawerStore";
import { notify } from "@/store/snackbarStore";
import { MQ } from "@/styles/responsive";
import {
  CR_CONTEXT_TYPE,
  DRAWER_WIDTHS,
  FILE_PROFILE_CONTEXT,
} from "@/utils/constants";
import { Box, useMediaQuery } from "@mui/material";
import { useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import React, { useMemo } from "react";
import useResponsiveDrawerWidth from "@/hooks/useResponsiveDrawerWidth";

export const Route = createFileRoute(
  "/_authenticated/ce-database/complaints/$complaintNumber"
)({
  component: React.memo(ComplaintProfilePage),
  notFoundComponent: () => <p>Complaint not found!</p>,
});

function ComplaintProfilePage(): React.ReactNode {
  const queryClient = useQueryClient();
  const { complaintNumber } = Route.useParams();
  const { setOpen, setClose } = useDrawer();
  const isMdToLg = useMediaQuery(MQ.mdToLg);
  

  const {
    status,
    data: complaintData,
    isError,
    error,
    isLoading,
  } = useComplaintByNumber(complaintNumber!);

  const { data: caseFileData } = useCaseFileByNumber(
    complaintData?.case_file.case_file_number ?? ""
  );

  const isUserEditAllowed = useIsRolesAllowed(
    [KC_USER_GROUPS.SUPERUSER],
    complaintData?.primary_officer ? [complaintData.primary_officer] : []
  );
  const showCreateCREntryButton =
    useIsRolesAllowed(
      [KC_USER_GROUPS.SUPERUSER],
      complaintData?.primary_officer ? [complaintData.primary_officer] : []
    ) && caseFileData?.case_file_status?.toLowerCase() === "open";

  const isComplaintEditable = useMemo(() => {
    return (
      isUserEditAllowed && complaintData?.status?.toLowerCase() === "open"
    );
  }, [complaintData?.status, isUserEditAllowed]);

  const drawerWidth = useResponsiveDrawerWidth(
    DRAWER_WIDTHS.COMPLAINT_DRAWER,
    { mdToLgMax: "750px" }
  );

  const handleOpenEditModal = () => {
    setOpen({
      content: (
        <ComplaintDrawer
          onSubmit={handleOnSubmit}
          complaint={complaintData}
          caseFile={caseFileData as CaseFile}
        />
      ),
      width: drawerWidth,
    });
  };

  const handleOnSubmit = (submitMsg: string) => {
    queryClient.invalidateQueries({
      queryKey: ["complaint", complaintNumber],
    });
    setClose();
    notify.success(submitMsg);
  };

  if (isError) return <ErrorPage error={error} />;

  return (
    <>
      {!complaintNumber || status === "pending" ? (
        <LoadingPage isLoading={isLoading} />
      ) : (
        <>
          <FileProfileHeader
            fileNumber={complaintNumber}
            status={complaintData.status}
            breadcrumbs={[
              { label: "Complaints", to: "/ce-database/complaints" },
              { label: complaintNumber },
            ]}
            profileContext={FILE_PROFILE_CONTEXT.COMPLAINT}
            caseFileNumber={caseFileData?.case_file_number}
          />
          <Box p={"1rem 1rem 1.25rem 3.75rem"} display={"flex"} gap={3} sx={{
            flexDirection: isMdToLg ? "column" : "row",
          }}>
            <ComplaintGeneralInformation
              complaintData={complaintData}
              onEdit={handleOpenEditModal}
              allowEdit={isComplaintEditable}
            />
            <ContinuationReport
              caseFileId={complaintData.case_file_id}
              contextType={CR_CONTEXT_TYPE.COMPLAINT}
              contextId={complaintData.id}
              allowCreateEntry={showCreateCREntryButton}
            />
          </Box>
        </>
      )}
    </>
  );
}
