import { request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  RestorativeJustice,
  RestorativeJusticeAPIData,
  RestorativeJusticeUpdateAPIData,
} from "@/models/RestorativeJustice";

const fetchRestorativeJustice = (
  inspectionId: number
): Promise<RestorativeJustice[]> => {
  return request({
    url: `/restorative-justices`,
    params: { inspection_id: inspectionId },
  });
};

const fetchRestorativeJusticeByNumber = (
  restorativeJusticeNumber: string
): Promise<RestorativeJustice[]> => {
  return request({
    url: `/restorative-justices/by-number/${restorativeJusticeNumber}`,
  });
};

const createRestorativeJustice = ({
  restorativeJustice,
}: {
  restorativeJustice: RestorativeJusticeAPIData;
}): Promise<RestorativeJustice> => {
  return request({
    url: "/restorative-justices",
    method: "post",
    data: restorativeJustice,
  });
};

const updateRestorativeJustice = ({
  restorativeJusticeId,
  restorativeJustice,
  inspectionId,
}: {
  restorativeJusticeId: number;
  restorativeJustice: RestorativeJusticeUpdateAPIData;
  inspectionId: number;
}): Promise<RestorativeJustice> => {
  return request({
    url: `/restorative-justices/${restorativeJusticeId}`,
    method: "patch",
    data: { ...restorativeJustice, inspection_id: inspectionId },
  });
};

const deleteRestorativeJustice = ({
  restorativeJusticeId,
}: {
  restorativeJusticeId: number;
}) => {
  return request({
    url: `/restorative-justices/${restorativeJusticeId}`,
    method: "delete",
  });
};

// Hooks
export const useFetchRestorativeJustice = (inspectionId: number) => {
  return useQuery({
    queryKey: ["inspection-restorative-justice", inspectionId],
    queryFn: () => fetchRestorativeJustice(inspectionId),
    enabled: !!inspectionId,
  });
};

export const useRestorativeJusticeByInspection = (inspectionId: number) => {
  return useQuery({
    queryKey: ["inspection-restorative-justice", inspectionId],
    queryFn: () => fetchRestorativeJustice(inspectionId),
    enabled: !!inspectionId,
  });
};

export const useFetchRestorativeJusticeByNumber = (
  restorativeJusticeNumber: string
) => {
  return useQuery({
    queryKey: ["restorative-justice-by-number", restorativeJusticeNumber],
    queryFn: () => fetchRestorativeJusticeByNumber(restorativeJusticeNumber),
    enabled: !!restorativeJusticeNumber,
  });
};

export const useCreateRestorativeJustice = (onSuccess: (data: RestorativeJustice) => void) => {
  return useMutation({ mutationFn: createRestorativeJustice, onSuccess });
};

export const useUpdateRestorativeJustice = (onSuccess: (data: RestorativeJustice) => void) => {
  return useMutation({ mutationFn: updateRestorativeJustice, onSuccess });
};

export const useDeleteRestorativeJustice = (onSuccess: (data: RestorativeJustice) => void) => {
  return useMutation({ mutationFn: deleteRestorativeJustice, onSuccess });
};

