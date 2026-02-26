import { yupResolver } from "@hookform/resolvers/yup";
import { Box, useMediaQuery } from "@mui/material";
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
import { StaffUser } from "@/models/Staff";
import dayjs from "dayjs";
import DrawerActionBarTop from "@/components/Shared/Drawer/DrawerActionBarTop";
import DrawerActionBarBottom from "@/components/Shared/Drawer/DrawerActionBarBottom";
import { CaseFile } from "@/models/CaseFile";
import { useCurrentLoggedInUser } from "@/hooks/useAuthorization";
import { MQ } from "@/styles/responsive";

type ComplaintDrawerProps = {
  onSubmit: (submitMsg: string) => void;
  caseFile: CaseFile;
  complaint?: Complaint;
};

const initFormData: ComplaintFormData = {
  concernDescription: "",
  locationDescription: "",
  topic: undefined,
  primaryOfficer: undefined,
  dateReceived: undefined,
  complaintSource: undefined,
  contactFullName: "",
  contactTitle: "",
  contactEmail: "",
  contactPhoneNumber: "",
  contactComments: "",
  agency: undefined,
  firstNation: undefined,
  otherDescription: "",
  allianceName: "",
  requirementSource: undefined,
  requirementSourceDescription: "",
  order: undefined,
};

const ComplaintDrawer: React.FC<ComplaintDrawerProps> = ({
  onSubmit,
  complaint,
  caseFile,
}) => {
  const { appHeaderHeight } = useMenuStore();
  const isMdToLg = useMediaQuery(MQ.mdToLg);

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
        topic: complaint.topic,
        dateReceived: complaint.date_received
          ? dayjs(complaint.date_received)
          : undefined,
        complaintSource: complaint.source_type,
        contactFullName: complaint.source_contact.full_name ?? "",
        contactTitle: complaint.source_contact.title ?? "",
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
        allianceName: complaint.source_contact?.alliance_name ?? "",
        requirementSource: complaint.requirement_source,
        requirementSourceDescription:
          complaint.requirement_source_description ?? "",
      };
    }
    const selectedOfficer = staffUserList.find(
      (user) => user.auth_user_guid === currentUser?.preferred_username
    );
    return {
      ...initFormData,
      primaryOfficer: selectedOfficer,
    };
  }, [agenciesList, complaint, firstNationsList, staffUserList, currentUser]);

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

  const { mutate: createComplaint, isPending: isCreateComplaintPending } =
    useCreateComplaint(onSuccess);
  const { mutate: updateComplaint, isPending: isUpdateComplaintPending } =
    useUpdateComplaint(onSuccess);

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
        <DrawerTitleBar
          title={complaint ? complaint.complaint_number : "Create Complaint"}
          isFormDirtyCheck
        />
        <DrawerActionBarTop
          isShowActionBar={!complaint}
          isLoading={isCreateComplaintPending}
        />
        <Box
          height={`calc(100vh - ${appHeaderHeight + 129}px)`} // 64px (DrawerTitleBar height) + 65px (DrawerActionBar height)
          sx={{
            display: "flex",
            flexDirection: isMdToLg ? "column" : "row",
            overflow: isMdToLg ? "auto" : "unset"
          }}
        >
          <ComplaintFormLeft
            staffUsersList={staffUserList ?? []}
            topicsList={topicsList ?? []}
            requirementSourceList={requirementSourceList ?? []}
            complaint={complaint}
            caseFileId={caseFile.id}
          />
          <Box
            sx={{
              width: isMdToLg ? "auto" : "399px",
              boxSizing: "border-box",
              overflow: isMdToLg? "unset" : "auto",
              margin: isMdToLg ? 2 : "unset"
            }}
          >
            <ComplaintSourceForm
              complaintSourceList={complaintSourceList ?? []}
              agenciesList={agenciesList ?? []}
              firstNationsList={firstNationsList ?? []}
            />
          </Box>
        </Box>
        <DrawerActionBarBottom
          isShowActionBar={!!complaint}
          isLoading={isUpdateComplaintPending}
        />
      </form>
    </FormProvider>
  );
};

export default ComplaintDrawer;
