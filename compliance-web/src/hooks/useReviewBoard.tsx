import {
  APReviewBoardItem,
  IRReviewBoardItem,
  OrderReviewBoardItem,
  WarningLetterReviewBoardItem,
} from "@/models/ReviewBoard";
import { request } from "@/utils/axiosUtils";
import { useQuery } from "@tanstack/react-query";


const fetchInspectionRecords = (): Promise<IRReviewBoardItem[]> => {
  return request({
    url: `/review-board/inspection-records`,
  });
};

const fetchOrderRecords = (): Promise<OrderReviewBoardItem[]> => {
  return request({
    url: `/review-board/orders`,
  });
};

const fetchWarningLetters = (): Promise<WarningLetterReviewBoardItem[]> => {
  return request({
    url: `/review-board/warning-letters`,
  });
};

const fetchAdministrativePenalties = (): Promise<APReviewBoardItem[]> => {
  return request({
    url: `/review-board/administrative-penalties`,
  });
};

export const useFetchInspectionRecords = () => {
  return useQuery({
    queryKey: ["review-board-inspection-records"],
    queryFn: fetchInspectionRecords,
  });
};

export const useFetchOrderRecords = () => {
  return useQuery({
    queryKey: ["review-board-order-records"],
    queryFn: fetchOrderRecords,
  });
};

export const useFetchWarningLetters = () => {
  return useQuery({
    queryKey: ["review-board-warning-letters"],
    queryFn: fetchWarningLetters,
  });
};

export const useFetchAdministrativePenalties = () => {
  return useQuery({
    queryKey: ["review-board-administrative-penalties"],
    queryFn: fetchAdministrativePenalties,
  });
};
