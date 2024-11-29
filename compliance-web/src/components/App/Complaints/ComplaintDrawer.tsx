import { yupResolver } from "@hookform/resolvers/yup";
import { Box, Stack } from "@mui/material";
import { FormProvider, useForm } from "react-hook-form";
import ComplaintFormLeft from "./ComplaintFormLeft";
import DrawerTitleBar from "@/components/Shared/Drawer/DrawerTitleBar";
import { useCallback, useMemo } from "react";
import { useMenuStore } from "@/store/menuStore";
import {
  formatComplaintData,
  ComplaintFormSchema,
  ComplaintSchemaType,
} from "./ComplaintFormUtils";
import {
  Complaint,
  ComplaintAPIData,
  ComplaintFormData,
} from "@/models/Complaint";
import {
  useComplaintSourcesData,
  useCreateComplaint,
  useRequirementSourcesData,
  useUpdateComplaint,
} from "@/hooks/useComplaints";
import { useAgenciesData } from "@/hooks/useAgencies";
import { useFirstNationsData } from "@/hooks/useFirstNations";
import { useTopicsData } from "@/hooks/useTopics";
import ComplaintSourceForm from "./ComplaintSourceForm";
import RequirementSourceForm from "./RequirementSourceForm";
import { StaffUser } from "@/models/Staff";
import dayjs from "dayjs";
import DrawerActionBarTop from "@/components/Shared/Drawer/DrawerActionBarTop";
import DrawerActionBarBottom from "@/components/Shared/Drawer/DrawerActionBarBottom";
import { CaseFile } from "@/models/CaseFile";
import { useCurrentLoggedInUser } from "@/hooks/useAuthorization";

type ComplaintDrawerProps = {
  onSubmit: (submitMsg: string) => void;
  caseFile: CaseFile;
  complaint?: Complaint;
};

const initFormData: ComplaintFormData = {
  project: undefined,
  dateReceived: undefined,
  primaryOfficer: undefined,
  complaintSource: undefined,
};

const ComplaintDrawer: React.FC<ComplaintDrawerProps> = ({
  onSubmit,
  complaint,
  caseFile,
}) => {
  const { appHeaderHeight } = useMenuStore();

  const { data: complaintSourceList } = useComplaintSourcesData();
  const { data: requirementSourceList } = useRequirementSourcesData();
  const { data: agenciesList } = useAgenciesData();
  const { data: firstNationsList } = useFirstNationsData();
  const { data: topicsList } = useTopicsData();
  const currentUser = useCurrentLoggedInUser();

  const staffUserList = Array.from(
    new Set(
      [caseFile.primary_officer, ...(caseFile.officers ?? [])]
        .filter(Boolean)
        .map((user) => user.id)
    )
  ).map((id) =>
    [caseFile.primary_officer, ...(caseFile.officers ?? [])].find(
      (user) => user?.id === id
    )
  ) as StaffUser[];

  const defaultValues = useMemo<ComplaintFormData>(() => {
    if (complaint) {
      return {
        concernDescription: complaint.concern_description,
        locationDescription: complaint.location_description,
        primaryOfficer: complaint.primary_officer,
        dateReceived: dayjs(complaint.date_received),
        complaintSource: complaint.source_type,
        contactFullName: complaint.source_contact.full_name ?? "",
        contactEmail: complaint.source_contact.email ?? "",
        contactPhoneNumber: complaint.source_contact.phone ?? "",
        contactComments: complaint.source_contact.comment ?? "",
        agency: agenciesList?.find(
          (item) => item.id === complaint.source_agency_id
        ),
        firstNation: firstNationsList?.find(
          (item) => item.id === complaint.source_first_nation_id
        ),
        otherDescription: complaint.source_contact?.description ?? "",
        requirementSource: complaint.requirement_source,
        topic: complaint.requirement_detail.topic,
        conditionNumber:
          complaint.requirement_detail?.additional_details?.condition_number ??
          "",
        conditionDescription: complaint.requirement_detail?.description ?? "",
        description: complaint.requirement_detail?.description ?? "",
        amendmentNumber:
          complaint.requirement_detail?.additional_details?.amendment_number ??
          "",
        amendmentConditionNumber:
          complaint.requirement_detail?.additional_details
            ?.amendment_condition_number ?? "",
      };
    }
    const selectedOfficer = staffUserList.find(
      (user) => user.auth_user_guid === currentUser?.preferred_username
    );
    return {
      ...initFormData,
      caseFileId: caseFile.id.toString(),
      primaryOfficer: selectedOfficer,
    };
  }, [
    agenciesList,
    complaint,
    firstNationsList,
    caseFile,
    staffUserList,
    currentUser,
  ]);

  const methods = useForm<ComplaintSchemaType>({
    resolver: yupResolver(ComplaintFormSchema),
    mode: "onBlur",
    defaultValues,
  });

  const { handleSubmit, reset } = methods;

  const onSuccess = useCallback(
    (data: Complaint) => {
      onSubmit(
        complaint
          ? "Changes saved successfully!"
          : `Complaint File ${data.complaint_number} was successfully created`
      );
      reset();
    },
    [complaint, onSubmit, reset]
  );

  const { mutate: createComplaint } = useCreateComplaint(onSuccess);
  const { mutate: updateComplaint } = useUpdateComplaint(onSuccess);

  const onSubmitHandler = useCallback(
    (formData: ComplaintSchemaType) => {
      if (complaint) {
        // update existing complaint record
        const complaintUpdateData: ComplaintAPIData =
          formatComplaintData(formData);
        updateComplaint({
          id: complaint.id,
          complaint: complaintUpdateData,
        });
      } else {
        const complaintData: ComplaintAPIData = formatComplaintData(
          formData,
          caseFile.id
        );
        createComplaint(complaintData);
      }
    },
    [complaint, updateComplaint, caseFile, createComplaint]
  );

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmitHandler)}>
        <DrawerTitleBar title="Create Complaint" isFormDirtyCheck />
        <DrawerActionBarTop isShowActionBar={!complaint} />
        <Stack
          height={`calc(100vh - ${appHeaderHeight + 129}px)`} // 64px (DrawerTitleBar height) + 65px (DrawerActionBar height)
          direction="row"
        >
          <ComplaintFormLeft staffUsersList={staffUserList ?? []} />
          <Box
            sx={{
              width: "399px",
              boxSizing: "border-box",
              overflow: "auto",
            }}
          >
            <ComplaintSourceForm
              complaintSourceList={complaintSourceList ?? []}
              agenciesList={agenciesList ?? []}
              firstNationsList={firstNationsList ?? []}
            />
            <RequirementSourceForm
              requirementSourceList={requirementSourceList ?? []}
              topicsList={topicsList ?? []}
            />
          </Box>
        </Stack>
        <DrawerActionBarBottom isShowActionBar={!!complaint} />
      </form>
    </FormProvider>
  );
};

export default ComplaintDrawer;
