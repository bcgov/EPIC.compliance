import {
  ContinuationReportAPIData,
  ContinuationReportExportAPIData,
  ContinuationReportPaginated,
} from "@/models/ContinuationReport";
import { OnSuccessType, request } from "@/utils/axiosUtils";
import { keepPreviousData, useMutation, useQuery } from "@tanstack/react-query";

const fetchContinuationReportEntries = (
  caseFileId: number,
  page: number,
  pageSize: number,
  searchText?: string,
): Promise<ContinuationReportPaginated> => {
  return request({
    url: "/continuation-reports",
    params: { case_file_id: caseFileId, page_no: page, page_size: pageSize, search_text: searchText },
  });
};

const createContinuationReportEntry = (crEntry: ContinuationReportAPIData) => {
  return request({
    url: "/continuation-reports",
    method: "post",
    data: crEntry,
  });
};

const continuationReportExport = (payload: ContinuationReportExportAPIData) => {
  return request({
    url: `/continuation-reports/render`,
    method: "POST",
    data: payload,
    responseType: "blob",
  });
};

const updateContinuationReportEntry = ({
  id,
  crEntry,
}: {
  id: number;
  crEntry: ContinuationReportAPIData;
}) => {
  return request({ url: `/continuation-reports/${id}`, method: "patch", data: crEntry });
};

const deleteContinuationReportEntry = (id: number) => {
  return request({ url: `/continuation-reports/${id}`, method: "delete" });
};

export const useCreateContinuationReportEntry = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createContinuationReportEntry, onSuccess });
};

export const useUpdateContinuationReportEntry = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateContinuationReportEntry, onSuccess });
};

export const useDeleteContinuationReportEntry = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: deleteContinuationReportEntry,
    onSuccess,
  });
};

export const useContinuationReportEntries = (
  caseFileId: number,
  page: number = 1,
  pageSize: number = 10,
  searchText?: string
) => {
  return useQuery({
    queryKey: ["continuation-reports", caseFileId, page, pageSize, searchText],
    queryFn: () => fetchContinuationReportEntries(caseFileId, page, pageSize, searchText),
    placeholderData: keepPreviousData,
    staleTime: Infinity,
    enabled: !!caseFileId,
  });
};

export const useContinuationReportExport = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: continuationReportExport, onSuccess });
};
