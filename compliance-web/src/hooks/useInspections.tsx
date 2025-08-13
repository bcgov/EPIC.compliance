import { Attendance, InspectionAttendance } from "@/models/Attendance";
import { Initiation } from "@/models/Initiation";
import {
  Inspection,
  InspectionAPIData,
  InspectionGridItems,
  InspectionGridQueryParams,
  InspectionMoreDetails,
  InspectionStatusAPIData,
} from "@/models/Inspection";
import { IRStatus } from "@/models/IRStatus";
import { IRType } from "@/models/IRType";
import { ProjectStatus } from "@/models/ProjectStatus";
import { OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useStaticQuery } from "@/hooks/useCustomQueries";

const fetchIRTypes = (): Promise<IRType[]> => {
  return request({ url: "/inspections/type-options" });
};

const fetchInitiations = (): Promise<Initiation[]> => {
  return request({ url: "/inspections/initiation-options" });
};

const fetchIRStatuses = (): Promise<IRStatus[]> => {
  return request({ url: "/inspections/ir-status-options" });
};

const fetchAttendanceOptions = (): Promise<Attendance[]> => {
  return request({ url: "/inspections/attendance-options" });
};

const fetchProjectStatuses = (): Promise<ProjectStatus[]> => {
  return request({ url: "/project-status-options" });
};

const fetchInspections = (
  queryParams?: InspectionGridQueryParams
): Promise<InspectionGridItems> => {
  return request({
    url: "/inspections",
    params: queryParams,
  });
};

const inspectionsExport = (
  queryParams: InspectionGridQueryParams = {}
) => {
  delete queryParams.page_no;
  delete queryParams.page_size;
  return request({
    method: "POST",
    url: `/inspections/export`,
    data: queryParams,
    responseType: "blob",
  });
};

const fetchInspectionsMoreDetails = (
  caseFileId: number
): Promise<InspectionMoreDetails[]> => {
  return request({
    url: `/inspections/more-details`,
    params: { case_file_id: caseFileId },
  });
};

const fetchInspection = (inspectionNumber: string): Promise<Inspection> => {
  return request({ url: `/inspections/ir-numbers/${inspectionNumber}` });
};

const fetchInspectionAttendances = (
  inspectionId: number
): Promise<InspectionAttendance[]> => {
  return request({ url: `/inspections/${inspectionId}/attendance-options` });
};

const createInspection = (inspection: InspectionAPIData) => {
  return request({ url: "/inspections", method: "post", data: inspection });
};

const updateInspection = ({
  id,
  inspection,
}: {
  id: number;
  inspection: InspectionAPIData;
}) => {
  return request({
    url: `/inspections/${id}`,
    method: "patch",
    data: inspection,
  });
};

const updateInspectionStatus = ({
  id,
  inspectionStatus,
}: {
  id: number;
  inspectionStatus: InspectionStatusAPIData;
}) => {
  return request({
    url: `/inspections/${id}/status`,
    method: "patch",
    data: inspectionStatus,
  });
};

const deleteInspection = (id: number) => {
  return request({ url: `/inspections/${id}`, method: "delete" });
};

export const useIRTypesData = () => {
  return useStaticQuery({
    queryKey: ["ir-types"],
    queryFn: fetchIRTypes,
  });
};

export const useInitiationsData = () => {
  return useStaticQuery({
    queryKey: ["inspections-initiations"],
    queryFn: fetchInitiations,
  });
};

export const useIRStatusesData = () => {
  return useStaticQuery({
    queryKey: ["ir-statuses"],
    queryFn: fetchIRStatuses,
  });
};

export const useAttendanceOptionsData = () => {
  return useStaticQuery({
    queryKey: ["attendance-options"],
    queryFn: fetchAttendanceOptions,
  });
};

export const useProjectStatusesData = () => {
  return useStaticQuery({
    queryKey: ["project-statuses"],
    queryFn: fetchProjectStatuses,
  });
};

export const useInspectionsData = (
  queryParams?: InspectionGridQueryParams
) => {
  return useQuery({
    queryKey: ["inspections", queryParams],
    queryFn: () => fetchInspections(queryParams),
  });
};

export const useInspectionsExport = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: inspectionsExport,
    onSuccess,
  });
};

export const useInspectionByNumber = (inspectionNumber: string) => {
  return useQuery({
    queryKey: ["inspection", inspectionNumber],
    queryFn: async () => {
      const inspection = await fetchInspection(inspectionNumber);
      const inspectionAttendances = await fetchInspectionAttendances(
        inspection?.id
      );
      return { ...inspection, inspectionAttendances };
    },
    enabled: !!inspectionNumber,
    staleTime: Infinity,
  });
};

export const useInspectionsByCaseFileId = (caseFileId: number) => {
  return useQuery({
    queryKey: ["inspections-by-caseFileId", caseFileId],
    queryFn: () => fetchInspections({ case_file_id: caseFileId.toString() }),
    enabled: !!caseFileId,
  });
};

export const useInspectionsMoreDetailsByCaseFileId = (caseFileId: number) => {
  return useQuery({
    queryKey: ["inspections-details-by-caseFileId", caseFileId],
    queryFn: () => fetchInspectionsMoreDetails(caseFileId),
    enabled: !!caseFileId,
  });
};

export const useCreateInspection = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createInspection, onSuccess });
};

export const useUpdateInspection = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateInspection, onSuccess });
};

export const useUpdateInspectionStatus = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateInspectionStatus, onSuccess });
};

export const useDeleteInspection = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: deleteInspection, onSuccess });
};
