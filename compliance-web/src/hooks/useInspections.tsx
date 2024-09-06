import { Inspection, InspectionAPIData } from "@/models/Inspection";
import { IRStatus } from "@/models/IRStatus";
import { IRType } from "@/models/IRType";
import { ProjectStatus } from "@/models/ProjectStatus";
import { OnErrorType, OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";


const fetchIRTypes = (): Promise<IRType[]> => {
  return request({ url: "/inspections/ir-type-options" });
};

const fetchIRStatuses = (): Promise<IRStatus[]> => {
  return request({ url: "/inspections/ir-status-options" });
};

const fetchProjectStatuses = (): Promise<ProjectStatus[]> => {
  return request({ url: "/project-status-options" });
};

const fetchInspections = (): Promise<Inspection[]> => {
  return request({ url: "/inspections" });
};

const createInspection = (inspection: InspectionAPIData) => {
  return request({ url: "/inspections", method: "post", data: inspection });
};

export const useIRTypesData = () => {
  return useQuery({
    queryKey: ["ir-types"],
    queryFn: fetchIRTypes,
  });
};

export const useIRStatusesData = () => {
  return useQuery({
    queryKey: ["ir-statuses"],
    queryFn: fetchIRStatuses,
  });
};

export const useProjectStatusesData = () => {
  return useQuery({
    queryKey: ["project-statuses"],
    queryFn: fetchProjectStatuses,
  });
};

export const useInspectionsData = () => {
  return useQuery({
    queryKey: ["inspections"],
    queryFn: fetchInspections,
  });
};

export const useCreateInspection = (
  onSuccess: OnSuccessType,
  onError: OnErrorType
) => {
  return useMutation({
    mutationFn: createInspection,
    onSuccess,
    onError,
  });
};
