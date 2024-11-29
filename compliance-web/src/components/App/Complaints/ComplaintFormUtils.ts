import { Agency } from "@/models/Agency";
import { ComplaintAPIData } from "@/models/Complaint";
import { ComplaintSource } from "@/models/ComplaintSource";
import { FirstNation } from "@/models/FirstNation";
import { RequirementSource } from "@/models/RequirementSource";
import { StaffUser } from "@/models/Staff";
import { Topic } from "@/models/Topic";
import {
  REGEX_EMAIL,
  REGEX_PHONE_NUMBER,
} from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { Dayjs } from "dayjs";
import * as yup from "yup";

export enum ComplaintSourceEnum {
  FIRST_NATION = "2",
  AGENCY = "3",
  OTHER = "4",
}

export enum RequirementSourceEnum {
  SCHEDULE_B = "1",
  EAC = "3",
  CPD = "4",
  ACT2018 = "5",
  COMPLAINCE_AGREEMENT = "6",
  ACT2022 = "7",
  NOT_EA_ACT = "8",
  OTHER = "9",
}

export const ComplaintFormSchema = yup.object().shape({
  concernDescription: yup
    .string()
    .nullable()
    .required("Concern Description is required"),
  locationDescription: yup.string().nullable(),
  primaryOfficer: yup.object<StaffUser>().nullable().required("Primary is required"),
  dateReceived: yup.mixed<Dayjs>().nullable().required("Date Received is required"),
  complaintSource: yup
    .object<ComplaintSource>()
    .nullable()
    .required("Complaint Source is required"),
  contactFullName: yup.string().nullable(),
  contactEmail: yup
    .string()
    .nullable()
    .test(
      "is-valid-email",
      "Invalid email format",
      (value) => !value || REGEX_EMAIL.test(value) // Only validate if value is not empty
    ),
  contactPhoneNumber: yup
    .string()
    .nullable()
    .test(
      "is-valid-phone",
      "Invalid phone number format",
      (value) => !value || REGEX_PHONE_NUMBER.test(value) // Only validate if value is not empty
    ),
  contactComments: yup.string().nullable(),
  agency: yup.object<Agency>().when("complaintSource", {
    is: (compSource: ComplaintSource) =>
      compSource?.id === ComplaintSourceEnum.AGENCY,
    then: (schema) => schema.required("Agency is required"),
    otherwise: (schema) => schema.notRequired(),
  }),
  firstNation: yup.object<FirstNation>().when("complaintSource", {
    is: (compSource: ComplaintSource) =>
      compSource?.id === ComplaintSourceEnum.FIRST_NATION,
    then: (schema) => schema.required("First Nation is required"),
    otherwise: (schema) => schema.notRequired(),
  }),
  otherDescription: yup.string().when("complaintSource", {
    is: (compSource: ComplaintSource) =>
      compSource?.id === ComplaintSourceEnum.OTHER,
    then: (schema) => schema.required("Description is required"),
    otherwise: (schema) => schema.notRequired(),
  }),
  requirementSource: yup.object<RequirementSource>().nullable(),
  conditionNumber: yup.string().when("requirementSource", {
    is: (reqSource: RequirementSource) =>
      reqSource?.id === RequirementSourceEnum.SCHEDULE_B,
    then: (schema) => schema.required("Condition Number is required"),
    otherwise: (schema) => schema.notRequired(),
  }),
  amendmentNumber: yup.string().nullable(),
  amendmentConditionNumber: yup.string().nullable(),
  description: yup.string().when("requirementSource", {
    is: (reqSource: RequirementSource) =>
      [RequirementSourceEnum.NOT_EA_ACT, RequirementSourceEnum.OTHER].includes(
        reqSource?.id as RequirementSourceEnum
      ),
    then: (schema) => schema.required("Description is required"),
    otherwise: (schema) => schema.notRequired(),
  }),
  conditionDescription: yup.string().when("requirementSource", {
    is: (reqSource: RequirementSource) =>
      [
        RequirementSourceEnum.EAC,
        RequirementSourceEnum.CPD,
        RequirementSourceEnum.ACT2018,
        RequirementSourceEnum.COMPLAINCE_AGREEMENT,
        RequirementSourceEnum.ACT2022,
      ].includes(reqSource?.id as RequirementSourceEnum),
    then: (schema) => schema.required("Condition Description is required"),
    otherwise: (schema) => schema.notRequired(),
  }),
  topic: yup
    .object<Topic>()
    .nullable()
    .when("requirementSource", {
      is: (reqSource: RequirementSource) => !!reqSource,
      then: (schema) => schema.required("Topic is required"),
      otherwise: (schema) => schema.notRequired(),
    }),
});

export type ComplaintSchemaType = yup.InferType<typeof ComplaintFormSchema>;

// Formatting inspection form data for API
export const formatComplaintData = (
  formData: ComplaintSchemaType,
  caseFileId?: number // as a flag for create new record
) => {
  const sourceId = (formData.complaintSource as ComplaintSource)?.id;
  const reqSourceId = (formData.requirementSource as RequirementSource)?.id;

  const complaintData: ComplaintAPIData = {
    primary_officer_id: (formData.primaryOfficer as StaffUser).id,
    location_description: formData.locationDescription ?? "",
    concern_description: formData.concernDescription ?? "",
    date_received: dateUtils.dateToISO(formData.dateReceived),
    source_type_id: sourceId,
    requirement_source_id: reqSourceId,
  };
  if (sourceId) {
    complaintData.complaint_source_contact = {
      full_name: formData.contactFullName ?? "",
      email: formData.contactEmail ?? "",
      phone: formData.contactPhoneNumber ?? "",
      comment: formData.contactComments ?? "",
    };
    switch (sourceId) {
      case ComplaintSourceEnum.FIRST_NATION:
        complaintData.source_first_nation_id = (
          formData.firstNation as FirstNation
        )?.id;
        break;
      case ComplaintSourceEnum.AGENCY:
        complaintData.source_agency_id = (formData.agency as Agency)?.id;
        break;
      case ComplaintSourceEnum.OTHER:
        complaintData.complaint_source_contact.description =
          formData.otherDescription ?? "";
        break;
    }
  }
  if (reqSourceId) {
    complaintData.requirement_source_details = {
      topic_id: (formData.topic as Topic)?.id,
    };
    switch (reqSourceId) {
      case RequirementSourceEnum.SCHEDULE_B:
        complaintData.requirement_source_details.condition_number =
          formData.conditionNumber ?? "";
        break;
      case RequirementSourceEnum.EAC:
        complaintData.requirement_source_details.amendment_condition_number =
          formData.amendmentConditionNumber ?? "";
        complaintData.requirement_source_details.amendment_number =
          formData.amendmentNumber ?? "";
        complaintData.requirement_source_details.description =
          formData.conditionDescription ?? "";
        break;
      case RequirementSourceEnum.NOT_EA_ACT:
      case RequirementSourceEnum.OTHER:
        complaintData.requirement_source_details.description =
          formData.description;
        break;
      case RequirementSourceEnum.ACT2018:
      case RequirementSourceEnum.ACT2022:
      case RequirementSourceEnum.CPD:
      case RequirementSourceEnum.COMPLAINCE_AGREEMENT:
        complaintData.requirement_source_details.description =
          formData.conditionDescription ?? "";
        break;
    }
  }
  complaintData.case_file_id = caseFileId ?? undefined; // map the fields only for create new record, and case file id is available
  return complaintData;
};
