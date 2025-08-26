import DrawerActionBarBottom from "@/components/Shared/Drawer/DrawerActionBarBottom";
import DrawerActionBarTop from "@/components/Shared/Drawer/DrawerActionBarTop";
import DrawerTitleBar from "@/components/Shared/Drawer/DrawerTitleBar";
import { useAgenciesData } from "@/hooks/useAgencies";
import { useCurrentLoggedInUser } from "@/hooks/useAuthorization";
import { useFirstNationsData } from "@/hooks/useFirstNations";
import {
  useAttendanceOptionsData,
  useCreateInspection,
  useInitiationsData,
  useIRTypesData,
  useProjectStatusesData,
  useUpdateInspection,
} from "@/hooks/useInspections";
import { useStaffUsersData } from "@/hooks/useStaff";
import { CaseFile } from "@/models/CaseFile";
import { Inspection, InspectionFormData } from "@/models/Inspection";
import { StaffUser } from "@/models/Staff";
import { useMenuStore } from "@/store/menuStore";
import { yupResolver } from "@hookform/resolvers/yup";
import { Stack } from "@mui/material";
import dayjs from "dayjs";
import { useCallback, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import InspectionFormLeft from "./InspectionFormLeft";
import InspectionFormRight from "./InspectionFormRight";
import { AttendanceEnum } from "@/utils/constants";
import {
  formatInspectionAPIData,
  InspectionFormSchema,
  InspectionSchemaType,
} from "./InspectionFormUtils";
import { Agency } from "@/models/Agency";
import { FirstNation } from "@/models/FirstNation";

type InspectionDrawerProps = {
  onSubmit: (submitMsg: string) => void;
  caseFile: CaseFile;
  inspection?: Inspection;
};

const initFormData: InspectionFormData = {
  project: undefined,
  primaryOfficer: undefined,
  irTypes: [],
  startDate: undefined,
  endDate: undefined,
  initiation: undefined,
  irStatus: undefined,
  projectStatus: undefined,
  caseFileId: undefined,
  isHistory: false,
  isIndependentEnvMonitor: false,
  isCHRepresentatives: false,
  officers: [],
  inAttendance: [],
  agencies: [],
  firstNations: [],
  municipal: "",
  other: "",
  projectDescription: "",
  locationDescription: "",
  utm: "",
  debriefDate: undefined,
};

const InspectionDrawer: React.FC<InspectionDrawerProps> = ({
  onSubmit,
  inspection,
  caseFile,
}) => {
  const { appHeaderHeight } = useMenuStore();

  const { data: initiationList } = useInitiationsData();
  const { data: irTypeList } = useIRTypesData();
  const { data: projectStatusList } = useProjectStatusesData();
  const { data: attendanceList } = useAttendanceOptionsData();
  const { data: agenciesList } = useAgenciesData();
  const { data: firstNationsList } = useFirstNationsData();
  const { data: inattendanceOfficersList } = useStaffUsersData();
  const currentUser = useCurrentLoggedInUser();

  const staffUserList = [
    caseFile.primary_officer,
    ...(caseFile.officers ?? []),
  ].filter(Boolean) as StaffUser[];

  const defaultValues = useMemo<InspectionFormData>(() => {
    if (inspection) {
      return {
        project: inspection.project,
        startDate: dayjs(inspection.start_date),
        endDate: dayjs(inspection.end_date),
        debriefDate: dayjs(inspection.debrief_date),
        primaryOfficer: inspection.primary_officer,
        initiation: inspection.initiation,
        irTypes: inspection.types,
        irStatus: inspection.ir_status,
        projectStatus: inspection.project_status,
        caseFileId: inspection.case_file_id?.toString(),
        isHistory: inspection.is_history ?? false,
        isIndependentEnvMonitor:
          inspection.inspectionAttendances?.some(
            (item) =>
              item.attendance_option_id ===
              Number(AttendanceEnum.INDIVIDUAL_ENV_MONITOR)
          ) ?? false,
        isCHRepresentatives:
          inspection.inspectionAttendances?.some(
            (item) =>
              item.attendance_option_id ===
              Number(AttendanceEnum.CH_RP_REPRESENTATIVE)
          ) ?? false,
        officers:
          (inspection.inspectionAttendances?.find(
            (item) =>
              item.attendance_option_id === Number(AttendanceEnum.OFFICERS)
          )?.data as StaffUser[]) ?? [],
        inAttendance:
          inspection.inspectionAttendances
            ?.filter(
              (item) =>
                ![
                  AttendanceEnum.INDIVIDUAL_ENV_MONITOR,
                  AttendanceEnum.CH_RP_REPRESENTATIVE,
                  AttendanceEnum.OFFICERS,
                ].includes(
                  item.attendance_option_id.toString() as AttendanceEnum
                )
            )
            .map((item) => item.attendance_option) ?? [],
        agencies:
          (inspection.inspectionAttendances?.find(
            (item) =>
              item.attendance_option_id === Number(AttendanceEnum.AGENCIES)
          )?.data as Agency[]) ?? [],
        firstNations:
          (inspection.inspectionAttendances?.find(
            (item) =>
              item.attendance_option_id === Number(AttendanceEnum.FIRST_NATIONS)
          )?.data as FirstNation[]) ?? [],
        municipal:
          (inspection.inspectionAttendances?.find(
            (item) =>
              item.attendance_option_id === Number(AttendanceEnum.MUNICIPAL)
          )?.data as string) ?? "",
        other:
          (inspection.inspectionAttendances?.find(
            (item) => item.attendance_option_id === Number(AttendanceEnum.OTHER)
          )?.data as string) ?? "",
        projectDescription: inspection.project_description ?? "",
        locationDescription: inspection.location_description ?? "",
        utm: inspection.utm ?? "",
      };
    }
    const selectedOfficer = staffUserList.find(
      (user) => user.auth_user_guid === currentUser?.preferred_username
    );
    return {
      ...initFormData,
      caseFileId: caseFile.id?.toString(),
      primaryOfficer: selectedOfficer,
      projectDescription: caseFile.project_description ?? "",
    };
  }, [inspection, caseFile, staffUserList, currentUser?.preferred_username]);

  const methods = useForm<InspectionSchemaType>({
    resolver: yupResolver(InspectionFormSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { handleSubmit, reset } = methods;

  const onSuccess = useCallback(
    (data: Inspection) => {
      onSubmit(
        inspection
          ? "Changes saved successfully!"
          : `Inspection File ${data.ir_number} was successfully created`
      );
      reset();
    },
    [inspection, onSubmit, reset]
  );

  const { mutate: createInspection, isPending: isCreateInspectionPending } =
    useCreateInspection(onSuccess);
  const { mutate: updateInspection, isPending: isUpdateInspectionPending } =
    useUpdateInspection(onSuccess);

  const onSubmitHandler = useCallback(
    (formData: InspectionSchemaType) => {
      if (inspection) {
        // update existing inspection record
        const inspectionUpdateData = formatInspectionAPIData(formData);
        updateInspection({
          id: inspection.id,
          inspection: inspectionUpdateData,
        });
      } else {
        const inspectionCreateData = formatInspectionAPIData(
          formData,
          caseFile.id
        );
        createInspection(inspectionCreateData);
      }
    },
    [inspection, updateInspection, caseFile, createInspection]
  );

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <DrawerTitleBar
          title={inspection ? inspection.ir_number : "Create Inspection"}
          isFormDirtyCheck
        />
        <DrawerActionBarTop
          isShowActionBar={!inspection}
          isLoading={isCreateInspectionPending}
        />
        <Stack
          height={`calc(100vh - ${appHeaderHeight + 129}px)`} // 64px (DrawerTitleBar height) + 65px (DrawerActionBar height)
          direction={"row"}
        >
          <InspectionFormLeft
            initiationList={initiationList ?? []}
            staffUsersList={staffUserList ?? []}
            irTypeList={irTypeList ?? []}
            projectStatusList={projectStatusList ?? []}
          />
          <InspectionFormRight
            attendanceList={attendanceList ?? []}
            agenciesList={agenciesList ?? []}
            firstNationsList={firstNationsList ?? []}
            staffList={inattendanceOfficersList ?? []}
          />
        </Stack>
        <DrawerActionBarBottom
          isShowActionBar={!!inspection}
          isLoading={isUpdateInspectionPending}
        />
      </form>
    </FormProvider>
  );
};

export default InspectionDrawer;
