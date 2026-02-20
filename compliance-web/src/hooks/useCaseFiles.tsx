import {
  CaseFile,
  CaseFileAPIData,
  CaseFileGridItems,
  CaseFileGridQueryParams,
  CaseFileStatusAPIData,
} from "@/models/CaseFile";
import { Initiation } from "@/models/Initiation";
import { StaffUser } from "@/models/Staff";
import { OnSuccessType, request } from "@/utils/axiosUtils";
import {
  UNAPPROVED_PROJECT_ABBREVIATION,
  UNAPPROVED_PROJECT_ID,
} from "@/utils/constants";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useStaticQuery } from "@/hooks/useCustomQueries";
import { CaseFileOption } from "@/models/CaseFile";
import { CaseFileOpenItems } from "@/models/CaseFileOpenItems";

const fetchCaseFiles = (
  queryParams?: CaseFileGridQueryParams
): Promise<CaseFileGridItems> => {
  return request({ url: "/case-files", params: queryParams });
};

const fetchCaseFileOptions = (): Promise<CaseFileOption[]> => {
  return request({ url: "/case-files/options" });
};

const fetchCaseFile = (caseFileNumber: string): Promise<CaseFile> => {
  return request({ url: `/case-files/case-file-numbers/${caseFileNumber}` });
};

const fetchOfficers = (caseFileId: number): Promise<StaffUser[]> => {
  return request({ url: `/case-files/${caseFileId}/officers` });
};

const fetchInitiations = (): Promise<Initiation[]> => {
  return request({ url: "/case-files/initiation-options" });
};

const fetchCaseFileLinks = (caseFileId: number): Promise<CaseFile[]> => {
  return request({ url: `/case-files/${caseFileId}/links` });
};

const fetchCaseFileOpenItems = (
  caseFileId: number
): Promise<CaseFileOpenItems> => {
  return request({ url: `/case-files/${caseFileId}/open-items` });
};

const createCaseFile = (caseFile: CaseFileAPIData) => {
  return request({ url: "/case-files", method: "post", data: caseFile });
};

const updateCaseFile = ({
  id,
  caseFile,
}: {
  id: number;
  caseFile: CaseFileAPIData;
}) => {
  return request({ url: `/case-files/${id}`, method: "patch", data: caseFile });
};

const updateCaseFileStatus = ({
  id,
  caseFileStatus,
}: {
  id: number;
  caseFileStatus: CaseFileStatusAPIData;
}) => {
  return request({
    url: `/case-files/${id}/status`,
    method: "patch",
    data: caseFileStatus,
  });
};

const deleteCaseFile = (id: number) => {
  return request({ url: `/case-files/${id}`, method: "delete" });
};

const linkCaseFile = ({ id, linkId }: { id: number; linkId: number }) => {
  return request({
    url: `/case-files/${id}/links`,
    method: "post",
    data: { link_case_file_id: linkId },
  });
};

const unlinkCaseFile = ({ id, linkId }: { id: number; linkId: number }) => {
  return request({
    url: `/case-files/${id}/unlink`,
    method: "patch",
    data: { case_file_to_unlink: linkId },
  });
};

const caseFilesExport = (queryParams: CaseFileGridQueryParams = {}) => {
  delete queryParams.page_no;
  delete queryParams.page_size;
  return request({
    method: "POST",
    url: `/case-files/export`,
    data: queryParams,
    responseType: "blob",
  });
};

export const useCaseFilesData = (queryParams?: CaseFileGridQueryParams) => {
  return useQuery({
    queryKey: ["case-files", queryParams],
    queryFn: () => fetchCaseFiles(queryParams),
  });
};

export const useCaseFileOptions = () => {
  return useQuery({
    queryKey: ["case-file-options"],
    queryFn: () => fetchCaseFileOptions(),
  });
};

export const useCaseFileByNumber = (caseFileNumber: string) => {
  return useQuery({
    queryKey: ["case-file", caseFileNumber],
    queryFn: async () => {
      const caseFile = await fetchCaseFile(caseFileNumber);
      const officers = await fetchOfficers(caseFile?.id);
      const caseFileLinks = await fetchCaseFileLinks(caseFile?.id);
      if (caseFile.project.abbreviation === UNAPPROVED_PROJECT_ABBREVIATION) {
        caseFile.project.id = UNAPPROVED_PROJECT_ID;
        delete caseFile.project.abbreviation;
      }
      return { ...caseFile, officers, caseFileLinks };
    },
    enabled: !!caseFileNumber,
    staleTime: Infinity,
  });
};

export const useCaseFileOpenItems = (caseFileId: number) => {
  return useQuery({
    queryKey: ["case-file-open-items", caseFileId],
    queryFn: () => fetchCaseFileOpenItems(caseFileId),
    enabled: !!caseFileId,
  });
};

export const useInitiationsData = () => {
  return useStaticQuery({
    queryKey: ["case-files-initiations"],
    queryFn: fetchInitiations,
  });
};

export const useCreateCaseFile = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createCaseFile, onSuccess });
};

export const useUpdateCaseFile = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateCaseFile, onSuccess });
};

export const useUpdateCaseFileStatus = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateCaseFileStatus, onSuccess });
};

export const useDeleteCaseFile = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: deleteCaseFile, onSuccess });
};

export const useLinkCaseFile = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: linkCaseFile, onSuccess });
};

export const useUnlinkCaseFile = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: unlinkCaseFile, onSuccess });
};

export const useCaseFilesExport = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: caseFilesExport, onSuccess });
};
