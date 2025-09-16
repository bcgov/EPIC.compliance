import DrawerActionBarBottom from "@/components/Shared/Drawer/DrawerActionBarBottom";
import DrawerActionBarTop from "@/components/Shared/Drawer/DrawerActionBarTop";
import DrawerTitleBar from "@/components/Shared/Drawer/DrawerTitleBar";
import { KC_USER_GROUPS, useIsRolesAllowed } from "@/hooks/useAuthorization";
import {
  useCreateCaseFile,
  useInitiationsData,
  useUpdateCaseFile,
} from "@/hooks/useCaseFiles";
import { useProjectsData } from "@/hooks/useProjects";
import { useStaffUsersData } from "@/hooks/useStaff";
import { CaseFile, CaseFileAPIData, CaseFileFormData } from "@/models/CaseFile";
import { Initiation } from "@/models/Initiation";
import { Project } from "@/models/Project";
import { StaffUser } from "@/models/Staff";
import router from "@/router/router";
import { useMenuStore } from "@/store/menuStore";
import { formatAuthorization } from "@/utils/appUtils";
import { UNAPPROVED_PROJECT_ID } from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { yupResolver } from "@hookform/resolvers/yup";
import { Box } from "@mui/material";
import dayjs, { Dayjs } from "dayjs";
import { useCallback, useEffect, useMemo } from "react";
import { FormProvider, useForm } from "react-hook-form";
import * as yup from "yup";
import CaseFileForm from "./CaseFileForm";

type CaseFileDrawerProps = {
  onSubmit: (submitMsg: string) => void;
  caseFile?: CaseFile;
};

const caseFileFormSchema = yup.object().shape({
  project: yup.object<Project>().nullable().required("Project is required"),
  authorization: yup.string().nullable(),
  regulatedParty: yup.string().nullable(),
  projectDescription: yup.string().nullable(),
  projectType: yup.string().nullable(),
  projectSubType: yup.string().nullable(),
  initiation: yup
    .object<Initiation>()
    .nullable()
    .required("Initiation is required"),
  primaryOfficer: yup
    .object<StaffUser>()
    .nullable()
    .required("Primary is required"),
  officers: yup.array().of(yup.object<StaffUser>()).nullable(),
  dateCreated: yup.mixed<Dayjs>().nullable(),
  caseFileNumber: yup.string().nullable(),
});

type CaseFileSchemaType = yup.InferType<typeof caseFileFormSchema>;

const initFormData: CaseFileFormData = {
  project: undefined,
  authorization: undefined,
  regulatedParty: undefined,
  projectDescription: undefined,
  projectType: undefined,
  projectSubType: undefined,
  dateCreated: undefined,
  primaryOfficer: undefined,
  officers: [],
  initiation: undefined,
  caseFileNumber: undefined,
};

const CaseFileDrawer: React.FC<CaseFileDrawerProps> = ({
  onSubmit,
  caseFile,
}) => {
  const { data: projectList } = useProjectsData({
    includeUnapproved: true,
  });
  const { data: initiationList } = useInitiationsData();
  const { data: staffUserList } = useStaffUsersData();
  const { appHeaderHeight } = useMenuStore();

  const isSuperUser = useIsRolesAllowed([KC_USER_GROUPS.SUPERUSER]);

  const defaultValues = useMemo<CaseFileFormData>(() => {
    if (caseFile) {
      return {
        project: caseFile.project,
        dateCreated: dayjs(caseFile.date_created),
        primaryOfficer: caseFile.primary_officer,
        officers: caseFile.officers,
        initiation: caseFile.initiation,
        caseFileNumber: caseFile.case_file_number,
        authorization: formatAuthorization(caseFile.authorization),
        regulatedParty: caseFile.regulated_party,
        projectDescription: caseFile.project_description ?? "",
        projectType: caseFile.type,
        projectSubType: caseFile.sub_type,
      };
    }
    return initFormData;
  }, [caseFile]);

  const methods = useForm<CaseFileSchemaType>({
    resolver: yupResolver(caseFileFormSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  const onSuccess = useCallback(
    (data: CaseFile) => {
      onSubmit(
        caseFile
          ? "Changes saved successfully."
          : `Case File ${data.case_file_number} was successfully created`
      );
      if (!caseFile) {
        router.navigate({
          to:`/ce-database/case-files/$caseFileNumber`,
          params: { caseFileNumber: data.case_file_number }
        });
      }
      reset();
    },
    [caseFile, onSubmit, reset]
  );

  const { mutate: createCaseFile, isPending: isCreateCaseFilePending } =
    useCreateCaseFile(onSuccess);
  const { mutate: updateCaseFile, isPending: isUpdateCaseFilePending } =
    useUpdateCaseFile(onSuccess);

  const getProjectId = (formData: CaseFileSchemaType) => {
    const projectId = (formData.project as Project)?.id ?? "";
    return projectId === UNAPPROVED_PROJECT_ID ? undefined : projectId;
  };

  const onSubmitHandler = useCallback(
    (data: CaseFileSchemaType) => {
      const projectId = getProjectId(data);
      let caseFileData: CaseFileAPIData = {
        project_id: projectId,
        initiation_id: (data.initiation as Initiation).id,
        primary_officer_id: (data.primaryOfficer as StaffUser).id,
        officer_ids:
          (data.officers as StaffUser[])?.map((user) => user.id) ?? [],
        date_created: dateUtils.dateToISO(data.dateCreated ?? dayjs()),
        case_file_number: data.caseFileNumber ?? undefined,
        project_description: data.projectDescription ?? "",
      };
      if (!projectId) {
        caseFileData = {
          ...caseFileData,
          unapproved_project_authorization: data.authorization ?? "",
          unapproved_project_regulated_party: data.regulatedParty ?? "",
          unapproved_project_type: data.projectType ?? "",
          unapproved_project_sub_type: data.projectSubType ?? "",
        };
      }
      if (caseFile) {
        updateCaseFile({ id: caseFile.id, caseFile: caseFileData });
      } else {
        createCaseFile(caseFileData);
      }
    },
    [caseFile, createCaseFile, updateCaseFile]
  );

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <DrawerTitleBar
          title={caseFile ? caseFile.case_file_number : "Create Case File"}
          isFormDirtyCheck
        />
        <DrawerActionBarTop
          isShowActionBar={!caseFile}
          isLoading={isCreateCaseFilePending}
        />
        <Box
          height={`calc(100vh - ${appHeaderHeight + 129}px)`} // 64px (DrawerTitleBar height) + 65px (DrawerActionBar height)
          overflow={"auto"}
        >
          <CaseFileForm
            projectList={projectList ?? []}
            initiationList={initiationList ?? []}
            staffUsersList={staffUserList ?? []}
            isEditMode={!!caseFile}
            isSuperUser={isSuperUser}
            caseFileProjectId={caseFile?.project_id}
          />
        </Box>
        <DrawerActionBarBottom
          isShowActionBar={!!caseFile}
          isLoading={isUpdateCaseFilePending}
        />
      </form>
    </FormProvider>
  );
};

export default CaseFileDrawer;
