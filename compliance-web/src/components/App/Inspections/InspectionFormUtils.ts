import { Agency } from "@/models/Agency";
import { Attendance } from "@/models/Attendance";
import { CaseFile } from "@/models/CaseFile";
import { FirstNation } from "@/models/FirstNation";
import { Initiation } from "@/models/Initiation";
import { Inspection, InspectionAPIData } from "@/models/Inspection";
import { IRType } from "@/models/IRType";
import { ProjectStatus } from "@/models/ProjectStatus";
import { StaffUser } from "@/models/Staff";
import { AttendanceEnum } from "@/utils/constants";
import dateUtils from "@/utils/dateUtils";
import { Dayjs } from "dayjs";
import * as yup from "yup";

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
  startDate: yup
    .mixed<Dayjs>()
    .required("Start date is required")
    .typeError("Invalid date")
    .test(
      "min-year",
      "Start date must be after year 1975",
      function (value) {
        if (!value) return true;
        return value.year() >= 1975;
      }
    ),
  endDate: yup
    .mixed<Dayjs>()
    .nullable()
    .typeError("Invalid date")
    .test(
      "end-after-start",
      "End date must be after start date",
      function (value) {
        const { startDate } = this.parent;
        if (!value || !startDate) return true;
        return value.isAfter(startDate) || value.isSame(startDate);
      }
    ),
  debriefDate: yup
    .mixed<Dayjs>()
    .nullable()
    .optional()
    .typeError("Invalid date"),
  initiation: yup
    .object<Initiation>()
    .nullable()
    .required("Initiation is required"),
  projectStatus: yup.object<ProjectStatus>().nullable(),
  officers: yup
    .array()
    .of(yup.object<StaffUser>())
    .nullable(),
  isHistory: yup.boolean().nullable(),
  isIndependentEnvMonitor: yup.boolean().nullable(),
  isCHRepresentatives: yup.boolean().nullable(),

  inAttendance: yup.array().of(yup.object<Attendance>()).nullable(),
  // Adding dynamic fields conditionally required based on `inAttendance` selection
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
});

export type InspectionSchemaType = yup.InferType<typeof InspectionFormSchema>;

// Formatting inspection form data for API
export const formatInspectionAPIData = (
  formData: InspectionSchemaType,
  caseFileId?: number // use as a flag for create new inspection mode
) => {
  const inAttendanceOptions =
    (formData.inAttendance as Attendance[])?.map((att) => att.id) ?? [];

  let inspectionData: InspectionAPIData = {
    is_history: formData.isHistory ?? false,
    project_description: formData.projectDescription ?? "",
    inspection_type_ids:
      (formData.irTypes as IRType[])?.map((ir) => ir.id) ?? [],
    initiation_id: (formData.initiation as Initiation).id,
    start_date: dateUtils.dateToISO(formData.startDate ?? new Date()),
    end_date: formData.endDate
      ? dateUtils.dateToISO(formData.endDate)
      : undefined,
    debrief_date: formData.debriefDate &&
      formData.debriefDate.isValid?.()
      ? dateUtils.dateToISO(formData.debriefDate)
      : undefined,
    primary_officer_id: (formData.primaryOfficer as StaffUser)?.id,
    location_description: formData.locationDescription ?? "",
    utm: formData.utm ?? "",
    project_status_id: (formData.projectStatus as ProjectStatus)?.id,
    attendance_option_ids: inAttendanceOptions,
  };

  if (formData.officers?.length) {
    inspectionData.attendance_option_ids?.push(AttendanceEnum.OFFICERS);
    inspectionData.attending_officer_ids =
      (formData.officers as StaffUser[])?.map((item) => item.id) ?? [];
  }

  if (formData.isIndependentEnvMonitor) {
    inspectionData.attendance_option_ids?.push(AttendanceEnum.INDIVIDUAL_ENV_MONITOR);
  }

  if (formData.isCHRepresentatives) {
    inspectionData.attendance_option_ids?.push(AttendanceEnum.CH_RP_REPRESENTATIVE);
  }

  if (inAttendanceOptions.length) {
    // Create an object to hold the attendance-related data
    const attendanceData: Partial<InspectionAPIData> = {};

    if (inAttendanceOptions.includes(AttendanceEnum.AGENCIES)) {
      attendanceData.agency_attendance_ids =
        (formData.agencies as Agency[])?.map((item) => item.id) ?? [];
    }

    if (inAttendanceOptions.includes(AttendanceEnum.FIRST_NATIONS)) {
      attendanceData.firstnation_attendance_ids =
        (formData.firstNations as FirstNation[])?.map((item) => item.id) ?? [];
    }

    if (inAttendanceOptions.includes(AttendanceEnum.OTHER)) {
      attendanceData.attendance_other = formData.other ?? "";
    }

    // Merge the attendance data with the inspection data
    inspectionData = {
      ...attendanceData,
      ...inspectionData,
    };
  }
  inspectionData.case_file_id = caseFileId ?? undefined; // map the fields only for create new inspection, and case file id is available

  return inspectionData;
};

export const formatInAttendance = (
  inspectionData?: Inspection,
  caseFileData?: CaseFile,
  isReport?: boolean
) => {
  let inAttendance = inspectionData?.inspectionAttendances;
  if (isReport) {
    inAttendance = inAttendance?.filter(
      (attendance) =>
        attendance.attendance_option.id !== AttendanceEnum.OFFICERS
    );
  }

  return inAttendance
    ?.map((attendance) => {
      if (attendance.data) {
        if (Array.isArray(attendance.data)) {
          return attendance.data.map((item) => item.name).join(", ");
        } else if (typeof attendance.data === "string") {
          return attendance.data;
        }
        return attendance.attendance_option.name;
      } else {
        if (
          attendance.attendance_option.id ===
          AttendanceEnum.CH_RP_REPRESENTATIVE
        ) {
          return caseFileData?.regulated_party ?? attendance.attendance_option.name;
        }
        return attendance.attendance_option.name;
      }
    })
    .join(", ") || "n/a";
};
