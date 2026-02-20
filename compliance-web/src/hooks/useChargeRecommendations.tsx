import { OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ChargeRecommendation,
  ChargeRecommendationAPIData,
  SentenceTypeOption,
} from "@/models/ChargeRecommendation";

const fetchChargeRecommendations = (
  inspectionId: number
): Promise<ChargeRecommendation[]> => {
  return request({
    url: `/charge-recommendations`,
    params: { inspection_id: inspectionId },
  });
};

const createChargeRecommendation = ({
  chargeRecommendation,
}: {
  chargeRecommendation: ChargeRecommendationAPIData;
}) => {
  return request({
    url: `/charge-recommendations`,
    method: "post",
    data: chargeRecommendation,
  });
};

const updateChargeRecommendation = ({
  chargeRecommendationId,
  chargeRecommendation,
}: {
  chargeRecommendationId: number;
  chargeRecommendation: ChargeRecommendationAPIData;
}) => {
  return request({
    url: `/charge-recommendations/${chargeRecommendationId}`,
    method: "patch",
    data: chargeRecommendation,
  });
};

const deleteChargeRecommendation = ({
  chargeRecommendationId,
}: {
  chargeRecommendationId: number;
}) => {
  return request({
    url: `/charge-recommendations/${chargeRecommendationId}`,
    method: "delete",
  });
};

const fetchSentenceTypeOptions = (): Promise<SentenceTypeOption[]> => {
  return request({ url: "/sentence-type-options" });
};

export const useSentenceTypeOptionsData = () => {
  return useQuery({
    queryKey: ["sentence-type-options"],
    queryFn: () => fetchSentenceTypeOptions(),
  });
};

export const useChargeRecommendationsData = (
  inspectionId: number,
  { isStaleInfinate = true }: { isStaleInfinate?: boolean } = {}
) => {
  return useQuery({
    queryKey: ["inspection-charge-recommendations", inspectionId],
    queryFn: () => fetchChargeRecommendations(inspectionId),
    enabled: !!inspectionId,
    staleTime: isStaleInfinate ? Infinity : 0,
  });
};

export const useCreateChargeRecommendation = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createChargeRecommendation, onSuccess });
};

export const useUpdateChargeRecommendation = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateChargeRecommendation, onSuccess });
};

export const useDeleteChargeRecommendation = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: deleteChargeRecommendation,
    onSuccess,
  });
};
