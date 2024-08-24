import { CaseFile, CaseFileAPIData } from "@/models/CaseFile";
import { Initiation } from "@/models/Initiation";
import { Project } from "@/models/Project";
import { OnErrorType, OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";


const fetchProjects = (): Promise<Project[]> => {
  return request({ url: "/projects" });
};

const fetchCaseFiles = (): Promise<CaseFile[]> => {
  return request({ url: "/case-files" });
};

const fetchInitiations = (): Promise<Initiation[]> => {
  return request({ url: "/case-files/initiation-options" });
};

const createCaseFile = (caseFile: CaseFileAPIData) => {
  return request({ url: "/case-files", method: "post", data: caseFile });
};

export const useProjectsData = () => {
  return useQuery({
    queryKey: ["projects"],
    queryFn: fetchProjects,
  });
};

export const useCaseFilesData = () => {
  return useQuery({
    queryKey: ["case-files"],
    queryFn: fetchCaseFiles,
  });
};

export const useInitiationsData = () => {
  return useQuery({
    queryKey: ["initiations"],
    queryFn: fetchInitiations,
  });
};

export const useCreateCaseFile = (
  onSuccess: OnSuccessType,
  onError: OnErrorType
) => {
  return useMutation({
    mutationFn: createCaseFile,
    onSuccess,
    onError,
  });
};
