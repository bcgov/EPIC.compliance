import { request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  ViolationTicket,
  ViolationTicketAPIData,
} from "@/models/ViolationTicket";

const fetchViolationTickets = (
  inspectionId: number
): Promise<ViolationTicket[]> => {
  return request({
    url: `/violation-tickets`,
    params: { inspection_id: inspectionId },
  });
};

const createViolationTicket = ({
  violationTicket,
}: {
  violationTicket: ViolationTicketAPIData;
}): Promise<ViolationTicket> => {
  return request({
    url: "/violation-tickets",
    method: "post",
    data: violationTicket,
  });
};

const updateViolationTicket = ({
  violationTicketId,
  violationTicket,
}: {
  violationTicketId: number;
  violationTicket: ViolationTicketAPIData;
}): Promise<ViolationTicket> => {
  return request({
    url: `/violation-tickets/${violationTicketId}`,
    method: "patch",
    data: violationTicket,
  });
};

const deleteViolationTicket = ({
  violationTicketId,
}: {
  violationTicketId: number;
}): Promise<void> => {
  return request({
    url: `/violation-tickets/${violationTicketId}`,
    method: "delete",
  });
};

// Hooks
export const useViolationTicketsData = (inspectionId: number) => {
  return useQuery({
    queryKey: ["inspection-violation-tickets", inspectionId],
    queryFn: () => fetchViolationTickets(inspectionId),
    enabled: !!inspectionId,
  });
};

export const useCreateViolationTicket = (onSuccess: (data: ViolationTicket) => void) => {
  return useMutation({ mutationFn: createViolationTicket, onSuccess });
};

export const useUpdateViolationTicket = (onSuccess: (data: ViolationTicket) => void) => {
  return useMutation({ mutationFn: updateViolationTicket, onSuccess });
};

export const useDeleteViolationTicket = (onSuccess: () => void) => {
  return useMutation<void, Error, { violationTicketId: number }>({ mutationFn: deleteViolationTicket, onSuccess });
};
