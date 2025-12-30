import { Agency } from "@/models/Agency";
import { ComplaintAPIData } from "@/models/Complaint";
import { ComplaintSource } from "@/models/ComplaintSource";
import { FirstNation } from "@/models/FirstNation";
import { InspectionOrder } from "@/models/InspectionOrder";
import { RequirementSource } from "@/models/RequirementSource";
import { StaffUser } from "@/models/Staff";
import { Topic } from "@/models/Topic";
import {
  REGEX_EMAIL,
  REGEX_PHONE_NUMBER,
  RequirementSourceEnum,
} from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { Dayjs } from "dayjs";
import * as yup from "yup";

export enum ComplaintSourceEnum {
  FIRST_NATION = "2",
  AGENCY = "3",
  OTHER = "4",
  FIRST_NATIONS_ALLIANCE = "5",
}

export enum ComplaintResolutionEnum {
  AGENCY = "2",
}

export const ComplaintFormSchema = yup.object().shape({
  concernDescription: yup
    .string()
    .nullable()
    .required("Concern Description is required"),
  locationDescription: yup.string().nullable(),
  topic: yup
    .object<Topic>()
    .nullable()
    .required("Topic is required"),
  primaryOfficer: yup.object<StaffUser>().nullable().required("Primary is required"),
  dateReceived: yup.mixed<Dayjs>().nullable().required("Date Received is required"),
  complaintSource: yup
    .object<ComplaintSource>()
    .nullable()
    .required("Complaint Source is required"),
  contactFullName: yup.string().nullable(),
  contactTitle: yup.string().nullable(),
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
  allianceName: yup.string().nullable().notRequired().when("complaintSource", {
    is: (compSource: ComplaintSource) =>
      compSource?.id === ComplaintSourceEnum.FIRST_NATIONS_ALLIANCE,
    then: (schema) => schema.notRequired().nullable(),
    otherwise: (schema) => schema.notRequired().nullable(),
  }),
  otherDescription: yup.string().when("complaintSource", {
    is: (compSource: ComplaintSource) =>
      compSource?.id === ComplaintSourceEnum.OTHER,
    then: (schema) => schema.required("Description is required"),
    otherwise: (schema) => schema.notRequired(),
  }),
  requirementSource: yup.object<RequirementSource>().nullable(),
  requirementSourceDescription: yup.string().nullable(),
  order: yup.object<InspectionOrder>().when("requirementSource", {
    is: (reqSource: RequirementSource) =>
      reqSource?.id === RequirementSourceEnum.ORDER,
    then: (schema) => schema.required("Order is required"),
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
    topic_id: (formData.topic as Topic)?.id,
    date_received: dateUtils.dateToISO(formData.dateReceived),
    source_type_id: sourceId,
    requirement_source_id: reqSourceId,
  };
  if (sourceId) {
    complaintData.complaint_source_contact = {
      full_name: formData.contactFullName ?? "",
      title: formData.contactTitle ?? "",
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
      case ComplaintSourceEnum.FIRST_NATIONS_ALLIANCE:
        complaintData.complaint_source_contact.alliance_name =
          formData.allianceName ?? "";
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
    if (reqSourceId === RequirementSourceEnum.ORDER && formData.order) {
      complaintData.requirement_source_details = {
        order_number: (formData.order as InspectionOrder)?.order_number ?? "",
      };
    } else {
      complaintData.requirement_source_description =
        formData.requirementSourceDescription ?? "";
    }
  }
  complaintData.case_file_id = caseFileId ?? undefined; // map the fields only for create new record, and case file id is available
  return complaintData;
};
