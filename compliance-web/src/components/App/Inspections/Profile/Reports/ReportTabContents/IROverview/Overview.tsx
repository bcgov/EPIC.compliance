import GridLabelValuePair from "@/components/Shared/GridLabelValuePair";
import { Grid } from "@mui/material";
import { useReportStore } from "@/components/App/Inspections/Profile/Reports/reportStore";
import { AttendanceEnum } from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { useCallback, useMemo } from "react";
import { StaffUser } from "@/models/Staff";
import { InspectionAttendance } from "@/models/Attendance";
import ProjectOverview from "./ProjectOverview";
import IRBoxContainer from "../IRBoxContainer";
import { useDrawer } from "@/store/drawerStore";
import { DRAWER_WIDTHS } from "@/utils/constants";
import { CaseFile } from "@/models/CaseFile";
import InspectionDrawer from "@/components/App/Inspections/InspectionDrawer";
import { notify } from "@/store/snackbarStore";
import { useQueryClient } from "@tanstack/react-query";
import { formatInAttendance } from "@/components/App/Inspections/InspectionFormUtils";
import { renderStaffNameWithPosition } from "@/utils/appUtils";
import useResponsiveDrawerWidth from "@/hooks/useResponsiveDrawerWidth";

const Overview = () => {
  const { inspectionData, caseFileData, isReportsReadOnly } = useReportStore();
  const { setOpen, setClose } = useDrawer();
  const queryClient = useQueryClient();

  const inAttendance = useMemo(
    () => formatInAttendance(inspectionData, caseFileData, true),
    [inspectionData, caseFileData]
  );

  const inspectingOfficers: StaffUser[] = useMemo(() => {
    const primaryOfficer = inspectionData?.primary_officer
      ? [inspectionData.primary_officer]
      : [];

    const attendingOfficers =
      inspectionData?.inspectionAttendances
        ?.filter(
          (attendance) =>
            attendance.attendance_option.id === AttendanceEnum.OFFICERS
        )
        .flatMap((attendance: InspectionAttendance) => {
          // Handle array of officers
          if (attendance.data && Array.isArray(attendance.data)) {
            return attendance.data as StaffUser[];
          }
          return [];
        }) ?? [];

    return [...primaryOfficer, ...attendingOfficers].filter(
      (officer): officer is StaffUser => officer !== null
    );
  }, [inspectionData]);

  const handleOnSubmit = useCallback(
    (submitMsg: string) => {
      queryClient.invalidateQueries({
        queryKey: ["inspection", inspectionData?.ir_number],
      });
      setClose();
      notify.success(submitMsg);
    },
    [queryClient, inspectionData, setClose]
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

  return (
    <>
      <ProjectOverview />
      <IRBoxContainer
        title="IR Overview"
        onEdit={!isReportsReadOnly ? handleOpenEditModal : undefined}
      >
        <Grid container spacing={1}>
          <GridLabelValuePair
            label="Project Status"
            value={inspectionData?.project_status?.name}
            gridProps={{ xs: 6 }}
          />
          <GridLabelValuePair
            label="Inspection Start"
            value={
              inspectionData?.start_date
                ? dateUtils.formatDate(inspectionData.start_date)
                : ""
            }
            gridProps={{ xs: 6 }}
          />
          <GridLabelValuePair
            label="Inspection Type"
            value={inspectionData?.types_text}
            gridProps={{ xs: 6 }}
          />
          <GridLabelValuePair
            label="Initiation"
            value={inspectionData?.initiation?.name}
            gridProps={{ xs: 6 }}
          />
          <GridLabelValuePair
            label="Project Description"
            value={inspectionData?.project_description}
            hideTooltip
            multiline
          />
          <GridLabelValuePair
            label="Location Description"
            value={inspectionData?.location_description}
            hideTooltip
            multiline
          />
          <GridLabelValuePair
            label="UTM"
            value={inspectionData?.utm}
            gridProps={{ xs: 6 }}
          />
          <GridLabelValuePair
            label="In Attendance"
            value={inAttendance}
            hideTooltip
            multiline
          />
          <GridLabelValuePair
            label="Inspecting Officer"
            value={inspectingOfficers.map((value, index) => (
              <span
                style={{ lineHeight: "normal", marginBottom: "4px" }}
                key={`${value.id}-${index}`}
              >
                {renderStaffNameWithPosition(value)}
              </span>
            ))}
            hideTooltip
            multiline
          />
        </Grid>
      </IRBoxContainer>
    </>
  );
};

export default Overview;
