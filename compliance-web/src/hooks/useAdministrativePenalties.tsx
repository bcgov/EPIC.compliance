import { OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  AdministrativePenalty,
  AdministrativePenaltyAPIData,
  AdministrativePenaltyLink,
} from "@/models/AdministrativePenalty";

const fetchAdministrativePenalties = (
  inspectionId: number
): Promise<AdministrativePenalty[]> => {
  return request({
    url: `/administrative-penalties`,
    params: { inspection_id: inspectionId },
  });
};

const fetchAdministrativePenaltiesByCaseFile = (
  caseFileId: number
): Promise<AdministrativePenalty[]> => {
  return request({
    url: `/administrative-penalties/projectwise`,
    params: { case_file_id: caseFileId },
  });
};

const fetchAdministrativePenaltyByNumber = (
  administrativePenaltyNumber: string
): Promise<AdministrativePenalty[]> => {
  return request({
    url: `/administrative-penalties/administrative-penalty-numbers/${administrativePenaltyNumber}`,
  });
};

const fetchAdministrativePenaltyLinks = (
  administrativePenaltyId: number
): Promise<AdministrativePenaltyLink[]> => {
  return request({
    url: `/administrative-penalties/${administrativePenaltyId}/links`
  });
};

const createAdministrativePenalty = ({
  administrativePenalty,
}: {
  administrativePenalty: AdministrativePenaltyAPIData;
}) => {
  return request({
    url: `/administrative-penalties`,
    method: "post",
    data: administrativePenalty,
  });
};

const updateAdministrativePenalty = ({
  administrativePenaltyId,
  administrativePenalty,
}: {
  administrativePenaltyId: number;
  administrativePenalty: AdministrativePenaltyAPIData;
}) => {
  return request({
    url: `/administrative-penalties/${administrativePenaltyId}`,
    method: "patch",
    data: administrativePenalty,
  });
};

const deleteAdministrativePenalty = ({
  administrativePenaltyId,
  inspectionId,
}: {
  administrativePenaltyId: number;
  inspectionId: number;
}) => {
  return request({
    url: `/administrative-penalties/${administrativePenaltyId}`,
    method: "delete",
    params: { inspection_id: inspectionId },
  });
};

const linkAdministrativePenalty = ({
  administrativePenaltyId,
  link,
}: {
  administrativePenaltyId: number;
  link: {
    inspection_id: number;
    inspection_requirement_ids: number[];
  };
}) => {
  return request({
    url: `/administrative-penalties/links`,
    method: "post",
    data: {
      administrative_penalty_id: administrativePenaltyId,
      inspection_id: link.inspection_id,
      inspection_requirement_ids: link.inspection_requirement_ids,
    },
  });
};

export const useAdministrativePenaltiesData = (
  inspectionId: number,
  { isStaleInfinate = true }: { isStaleInfinate?: boolean } = {}
) => {
  return useQuery({
    queryKey: ["inspection-administrative-penalties", inspectionId],
    queryFn: () => fetchAdministrativePenalties(inspectionId),
    enabled: !!inspectionId,
    staleTime: isStaleInfinate ? Infinity : 0,
  });
};

export const useAdministrativePenaltyLinksData = (
  administrativePenaltyId: number,
  { isStaleInfinate = true }: { isStaleInfinate?: boolean } = {}
) => {
  return useQuery({
    queryKey: ["administrative-penalty-links", administrativePenaltyId],
    queryFn: () => fetchAdministrativePenaltyLinks(administrativePenaltyId),
    enabled: !!administrativePenaltyId,
    staleTime: isStaleInfinate ? Infinity : 0,
  });
};

export const useAdministrativePenaltiesByCaseFileData = (
  caseFileId: number,
  { isStaleInfinate = true }: { isStaleInfinate?: boolean } = {}
) => {
  return useQuery({
    queryKey: ["projectwise-administrative-penalties", caseFileId],
    queryFn: () => fetchAdministrativePenaltiesByCaseFile(caseFileId),
    enabled: !!caseFileId,
    staleTime: isStaleInfinate ? Infinity : 0,
  });
};

export const useFetchAdministrativePenaltyByNumber = (
  onSuccess: OnSuccessType
) => {
  return useMutation({
    mutationFn: fetchAdministrativePenaltyByNumber,
    onSuccess,
  });
};

export const useCreateAdministrativePenalty = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createAdministrativePenalty, onSuccess });
};

export const useUpdateAdministrativePenalty = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateAdministrativePenalty, onSuccess });
};

export const useDeleteAdministrativePenalty = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: deleteAdministrativePenalty,
    onSuccess,
  });
};

export const useLinkAdministrativePenalty = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: linkAdministrativePenalty,
    onSuccess,
  });
};
