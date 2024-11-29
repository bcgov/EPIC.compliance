import { Agency } from "@/models/Agency";
import { Attendance } from "@/models/Attendance";
import { DateRange } from "@/models/DateRange";
import { FirstNation } from "@/models/FirstNation";
import { Initiation } from "@/models/Initiation";
import { InspectionAPIData } from "@/models/Inspection";
import { IRStatus } from "@/models/IRStatus";
import { IRType } from "@/models/IRType";
import { ProjectStatus } from "@/models/ProjectStatus";
import { StaffUser } from "@/models/Staff";
import dateUtils from "@/utils/dateUtils";
import { Dayjs } from "dayjs";
import * as yup from "yup";

export enum AttendanceEnum {
  AGENCIES = "1",
  FIRST_NATIONS = "2",
  MUNICIPAL = "3",
  OTHER = "7",
  OFFICERS = "8",
}

export const InspectionFormSchema = yup.object().shape({
  projectDescription: yup.string().nullable(),
  locationDescription: yup.string().nullable(),
  utm: yup.string().nullable(),
  primaryOfficer: yup
    .object<StaffUser>()
    .nullable()
    .required("Primary is required"),
  irTypes: yup
    .array()
    .of(yup.object<IRType>())
    .min(1, "At least one Type is required")
    .required("Type is required"),
  dateRange: yup
    .object<DateRange>()
    .shape({
      startDate: yup
        .mixed<Dayjs>()
        .required("Start date is required")
        .typeError("Invalid date"),
      endDate: yup
        .mixed<Dayjs>()
        .required("End date is required")
        .typeError("Invalid date")
      // .min(yup.ref("startDate"), "End date cannot be before start date"),
    })
    .test(
      "required",
      "Date is required",
      (value) => !!value?.startDate || !!value?.endDate
    )
    .nullable(),
  initiation: yup
    .object<Initiation>()
    .nullable()
    .required("Initiation is required"),
  irStatus: yup.object<IRStatus>().nullable(),
  projectStatus: yup.object<ProjectStatus>().nullable(),

  inAttendance: yup.array().of(yup.object<Attendance>()).nullable(),

  // Adding dynamic fields conditionally required based on `inAttendance` selection
  municipal: yup
    .string()
    .nullable()
    .when("inAttendance", {
      is: (attendance: Attendance[]) =>
        attendance?.some((item) => item.id === AttendanceEnum.MUNICIPAL),
      then: (schema) => schema.required("Municipal is required"),
      otherwise: (schema) => schema.notRequired(),
    }),

  other: yup
    .string()
    .nullable()
    .when("inAttendance", {
      is: (attendance: Attendance[]) => {
        return attendance?.some((item) => item.id === AttendanceEnum.OTHER);
      },
      then: (schema) => schema.required("Other is required"),
      otherwise: (schema) => schema.notRequired(),
    }),

  firstNations: yup
    .array()
    .of(yup.object<FirstNation>())
    .nullable()
    .when("inAttendance", {
      is: (attendance: Attendance[]) =>
        attendance?.some((item) => item.id === AttendanceEnum.FIRST_NATIONS),
      then: (schema) =>
        schema
          .min(1, "At least one First Nation is required")
          .required("First Nations is required"),
      otherwise: (schema) => schema.notRequired(),
    }),

  agencies: yup
    .array()
    .of(yup.object<Agency>())
    .nullable()
    .when("inAttendance", {
      is: (attendance: Attendance[]) =>
        attendance?.some((item) => item.id === AttendanceEnum.AGENCIES),
      then: (schema) =>
        schema
          .min(1, "At least one Agency is required")
          .required("Agencies are required"),
      otherwise: (schema) => schema.notRequired(),
    }),

  officers: yup
    .array()
    .of(yup.object<StaffUser>())
    .nullable()
    .when("inAttendance", {
      is: (attendance: Attendance[]) =>
        attendance?.some((item) => item.id === AttendanceEnum.OFFICERS),
      then: (schema) =>
        schema
          .min(1, "At least one Officer is required")
          .required("Officers are required"),
      otherwise: (schema) => schema.notRequired(),
    }),
});

export type InspectionSchemaType = yup.InferType<typeof InspectionFormSchema>;

// Formatting inspection form data for API
export const formatInspectionData = (
  formData: InspectionSchemaType,
  caseFileId?: number // use as a flag for create new inspection mode
) => {
  const inAttendanceOptions =
    (formData.inAttendance as Attendance[])?.map((att) => att.id) ?? [];

  let inspectionData: InspectionAPIData = {
    project_description: formData.projectDescription ?? "",
    inspection_type_ids:
      (formData.irTypes as IRType[])?.map((ir) => ir.id) ?? [],
    initiation_id: (formData.initiation as Initiation).id,
    start_date: dateUtils.dateToISO(
      formData.dateRange?.startDate ?? new Date()
    ),
    end_date: dateUtils.dateToISO(
      formData.dateRange?.endDate ?? new Date()
    ),
    primary_officer_id: (formData.primaryOfficer as StaffUser)?.id,
    location_description: formData.locationDescription ?? "",
    utm: formData.utm ?? "",
    ir_status_id: (formData.irStatus as IRStatus)?.id,
    project_status_id: (formData.projectStatus as ProjectStatus)?.id,
    attendance_option_ids: inAttendanceOptions,
  };
  if (inAttendanceOptions.length) {
    inspectionData = {
      agency_attendance_ids:
        (formData.agencies as Agency[])?.map((item) => item.id) ?? [],
      firstnation_attendance_ids:
        (formData.firstNations as FirstNation[])?.map((item) => item.id) ?? [],
      attending_officer_ids:
        (formData.officers as StaffUser[])?.map((item) => item.id) ?? [],
      attendance_municipal: formData.municipal ?? "",
      attendance_other: formData.other ?? "",
      ...inspectionData,
    };
  }
  inspectionData.case_file_id = caseFileId ?? undefined; // map the fields only for create new inspection, and case file id is available

  return inspectionData;
};
