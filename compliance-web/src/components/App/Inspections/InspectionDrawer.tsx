import { useStaffUsersData } from "@/hooks/useStaff";
import { useProjectsData } from "@/hooks/useProjects";
import { CaseFile } from "@/models/CaseFile";
import { StaffUser } from "@/models/Staff";
import { yupResolver } from "@hookform/resolvers/yup";
import { Box, Button, Stack } from "@mui/material";
import { BCDesignTokens } from "epic.theme";
import { FormProvider, useForm } from "react-hook-form";
import InspectionFormLeft from "./InspectionFormLeft";
import DrawerTitleBar from "@/components/Shared/Drawer/DrawerTitleBar";
import { useCallback, useEffect, useMemo, useRef } from "react";
import { useMenuStore } from "@/store/menuStore";
import {
  useAttendanceOptionsData,
  useCreateInspection,
  useInitiationsData,
  useIRStatusesData,
  useIRTypesData,
  useProjectStatusesData,
} from "@/hooks/useInspections";
import {
  Inspection,
  InspectionAPIData,
  InspectionFormData,
} from "@/models/Inspection";
import InspectionFormRight from "./InspectionFormRight";
import { useModal } from "@/store/modalStore";
import LinkCaseFileModal from "@/components/App/CaseFiles/LinkCaseFileModal";
import { useAgenciesData } from "@/hooks/useAgencies";
import { useFirstNationsData } from "@/hooks/useFirstNations";
import {
  formatInspectionData,
  getProjectId,
  InspectionFormSchema,
  InspectionSchemaType,
} from "./InspectionFormUtils";
import { INITIATION } from "@/utils/constants";

type InspectionDrawerProps = {
  onSubmit: (submitMsg: string) => void;
  inspection?: CaseFile;
};

const initFormData: InspectionFormData = {
  project: undefined,
  dateRange: undefined,
  leadOfficer: undefined,
  officers: [],
  irTypes: [],
  initiation: undefined,
  irStatus: undefined,
  projectStatus: undefined,
  caseFileId: undefined,
};

const InspectionDrawer: React.FC<InspectionDrawerProps> = ({
  onSubmit,
  inspection,
}) => {
  const { appHeaderHeight } = useMenuStore();
  const drawerTopRef = useRef<HTMLDivElement | null>(null);

  const { setOpen: setModalOpen, setClose: setModalClose } = useModal();

  const { data: projectList } = useProjectsData({ includeUnapproved: true });
  const { data: initiationList } = useInitiationsData();
  const { data: staffUserList } = useStaffUsersData();
  const { data: irTypeList } = useIRTypesData();
  const { data: irStatusList } = useIRStatusesData();
  const { data: projectStatusList } = useProjectStatusesData();
  const { data: attendanceList } = useAttendanceOptionsData();
  const { data: agenciesList } = useAgenciesData();
  const { data: firstNationsList } = useFirstNationsData();

  const defaultValues = useMemo<InspectionFormData>(() => {
    if (inspection) {
      // TDOD: Map existing data
    }
    return initFormData;
  }, [inspection]);

  const methods = useForm<InspectionSchemaType>({
    resolver: yupResolver(InspectionFormSchema),
    mode: "onBlur",
    defaultValues,
  });

  const {
    handleSubmit,
    reset,
    formState: { isValid },
    getValues,
  } = methods;

  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  const onSuccess = useCallback(
    (data: Inspection) => {
      onSubmit(
        inspection
          ? "Successfully updated!"
          : `Inspection File ${data.ir_number} was successfully created`
      );
      reset();
    },
    [inspection, onSubmit, reset]
  );

  const { mutate: createInspection } = useCreateInspection(onSuccess);

  const addOrUpdateInspection = useCallback(
    (caseFileId: number) => {
      const formData = getValues();
      const inspectionData: InspectionAPIData = formatInspectionData(
        formData,
        caseFileId
      );

      if (inspection) {
        // TODO: Add update logic here
      } else {
        createInspection(inspectionData);
      }
    },
    [createInspection, getValues, inspection]
  );

  const handleOnCaseFileSubmit = useCallback(
    (caseFileId: number) => {
      addOrUpdateInspection(caseFileId);
      setModalClose();
    },
    [addOrUpdateInspection, setModalClose]
  );

  const onSubmitHandler = useCallback(
    (data: InspectionSchemaType) => {
      // Open modal for linking or creating case file
      setModalOpen({
        content: (
          <LinkCaseFileModal
            onSubmit={handleOnCaseFileSubmit}
            projectId={getProjectId(data)}
            leadOfficerId={(data.leadOfficer as StaffUser)?.id}
            initiationId={INITIATION.INSPECTION_ID}
          />
        ),
      });
    },
    [setModalOpen, handleOnCaseFileSubmit]
  );

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <Box ref={drawerTopRef}>
          <DrawerTitleBar title="Create Inspection" isFormDirtyCheck />
          <Box
            sx={{
              backgroundColor: BCDesignTokens.surfaceColorBackgroundLightGray,
              padding: "0.75rem 2rem",
              textAlign: "right",
            }}
          >
            <Button type="submit" disabled={!isValid}>
              Create
            </Button>
          </Box>
        </Box>

        <Stack
          height={`calc(100vh - ${(drawerTopRef.current?.offsetHeight ?? 120) + appHeaderHeight}px)`}
          direction={"row"}
        >
          <InspectionFormLeft
            projectList={projectList ?? []}
            initiationList={initiationList ?? []}
            staffUsersList={staffUserList ?? []}
            irTypeList={irTypeList ?? []}
          />
          <InspectionFormRight
            irStatusList={irStatusList ?? []}
            projectStatusList={projectStatusList ?? []}
            attendanceList={attendanceList ?? []}
            agenciesList={agenciesList ?? []}
            firstNationsList={firstNationsList ?? []}
          />
        </Stack>
      </form>
    </FormProvider>
  );
};

export default InspectionDrawer;
