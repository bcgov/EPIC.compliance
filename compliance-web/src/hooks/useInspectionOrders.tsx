import { OnErrorType, OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  InspectionOrder,
  InspectionOrderAPIData,
} from "@/models/InspectionOrder";
import { OrderApproval } from "@/models/OrderApproval";
import { OrderStatusEnum } from "@/utils/constants";

const fetchInspectionOrders = (
  inspectionId: number
): Promise<InspectionOrder[]> => {
  return request({ url: `/orders`, params: { inspection_id: inspectionId } });
};

const fetchInspectionOrdersProjectwise = (
  caseFileId: number
): Promise<InspectionOrder[]> => {
  return request({
    url: `/orders/projectwise`,
    params: { case_file_id: caseFileId },
  });
};

const fetchInspectionOrderByNumber = (
  orderNumber: string
): Promise<InspectionOrder> => {
  return request({
    url: `orders/order-numbers/${orderNumber}`,
  });
};

const createInspectionOrder = ({
  inspectionOrder,
}: {
  inspectionOrder: InspectionOrderAPIData;
}) => {
  return request({
    url: `/orders`,
    method: "post",
    data: inspectionOrder,
  });
};

const updateInspectionOrder = ({
  inspectionOrderId,
  inspectionOrder,
}: {
  inspectionOrderId: number;
  inspectionOrder: InspectionOrderAPIData;
}) => {
  return request({
    url: `/orders/${inspectionOrderId}`,
    method: "patch",
    data: inspectionOrder,
  });
};

const inspectionOrderRender = ({
  inspectionOrderId,
  format,
}: {
  inspectionOrderId: number;
  format: "html" | "pdf";
}) => {
  // If requesting PDF, specify responseType as 'blob'
  const responseType = format === "pdf" ? "blob" : "json";

  return request({
    method: "POST",
    url: `/orders/${inspectionOrderId}/render`,
    data: { output_format: format },
    responseType: responseType,
  });
};

const createOrderApproval = ({
  inspectionOrderId,
  approvalPayload,
}: {
  inspectionOrderId: number;
  approvalPayload: {
    approved_by_id?: number;
  };
}) => {
  return request({
    url: `/orders/${inspectionOrderId}/approvals`,
    method: "post",
    data: approvalPayload,
  });
};

const fetchOrderApprovals = ({
  inspectionOrderId,
}: {
  inspectionOrderId: number;
}): Promise<OrderApproval[]> => {
  return request({
    url: `/orders/${inspectionOrderId}/approvals`,
  });
};

const updateOrderApprovalStatus = ({
  inspectionOrderId,
  approvalId,
  statusPayload,
}: {
  inspectionOrderId: number;
  approvalId: number;
  statusPayload: {
    approval_status: string;
    approved_by_id: number;
  };
}) => {
  return request({
    url: `/orders/${inspectionOrderId}/approvals/${approvalId}/status`,
    method: "patch",
    data: statusPayload,
  });
};

const issueOrder = ({
  inspectionOrderId,
  issuePayload,
}: {
  inspectionOrderId: number;
  issuePayload: {
    date_issued: string;
  };
}) => {
  return request({
    url: `/orders/${inspectionOrderId}/issue`,
    method: "patch",
    data: issuePayload,
  });
};

const deleteInspectionOrder = ({
  inspectionOrderId,
}: {
  inspectionOrderId: number;
}) => {
  return request({
    url: `/orders/${inspectionOrderId}`,
    method: "delete",
  });
};

const updateOrderStatus = ({
  inspectionOrderId,
  statusPayload,
}: {
  inspectionOrderId: number;
  statusPayload: {
    status: string;
  };
}) => {
  return request({
    url: `/orders/${inspectionOrderId}/status`,
    method: "patch",
    data: statusPayload,
  });
};

const replaceOrder = ({
  inspectionOrderId,
  replacementOrderNumber = "",
}: {
  inspectionOrderId: number;
  replacementOrderNumber?: string;
}) => {
  return request({
    url: `/orders/${inspectionOrderId}/replace`,
    method: "post",
    data: replacementOrderNumber
      ? {
          replacement_order_number: replacementOrderNumber,
        }
      : {},
  });
};

const resetOrderTemplate = ({
  inspectionOrderId,
  fieldNames,
}: {
  inspectionOrderId: number;
  fieldNames: string[];
}) => {
  return request({
    url: `/orders/${inspectionOrderId}/reset`,
    method: "patch",
    data: {
      field_names: fieldNames,
    },
  });
};

export const useInspectionOrdersData = (
  inspectionId: number,
  {
    filterOpenOrders = false,
    isStaleInfinate = true,
  }: { filterOpenOrders?: boolean; isStaleInfinate?: boolean } = {}
) => {
  return useQuery({
    queryKey: ["inspection-orders", inspectionId],
    queryFn: () => fetchInspectionOrders(inspectionId),
    select: (data) => {
      if (filterOpenOrders) {
        return data.filter(
          (order) => order.order_status?.id === OrderStatusEnum.OPEN
        );
      }
      return data;
    },
    enabled: !!inspectionId,
    staleTime: isStaleInfinate ? Infinity : 0,
  });
};

export const useInspectionOrdersProjectwiseData = (caseFileId: number) => {
  return useQuery({
    queryKey: ["inspection-orders-projectwise", caseFileId],
    queryFn: () => fetchInspectionOrdersProjectwise(caseFileId),
    select: (data) => {
      return data.filter(
        (order) => order.order_status?.id === OrderStatusEnum.OPEN
      );
    },
    enabled: !!caseFileId,
    staleTime: Infinity,
  });
};

export const useInspectionOrderByNumber = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: fetchInspectionOrderByNumber,
    onSuccess,
  });
};

export const useCreateInspectionOrder = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createInspectionOrder, onSuccess });
};

export const useUpdateInspectionOrder = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateInspectionOrder, onSuccess });
};

export const useInspectionOrderRendered = (
  onSuccess: OnSuccessType,
  onError: OnErrorType
) => {
  return useMutation({
    mutationFn: inspectionOrderRender,
    onSuccess,
    onError,
  });
};

export const useCreateOrderApproval = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: createOrderApproval,
    onSuccess,
  });
};

export const useFetchOrderApprovals = (inspectionOrderId: number) => {
  return useQuery({
    queryKey: ["order-approvals", inspectionOrderId],
    queryFn: () => fetchOrderApprovals({ inspectionOrderId }),
    enabled: !!inspectionOrderId,
    staleTime: Infinity,
  });
};

export const useUpdateOrderApprovalStatus = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: updateOrderApprovalStatus,
    onSuccess,
  });
};

export const useIssueOrder = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: issueOrder,
    onSuccess,
  });
};

export const useDeleteInspectionOrder = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: deleteInspectionOrder,
    onSuccess,
  });
};

export const useUpdateOrderStatus = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: updateOrderStatus,
    onSuccess,
  });
};

export const useReplaceOrder = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: replaceOrder,
    onSuccess,
  });
};

export const useResetOrderTemplate = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: resetOrderTemplate,
    onSuccess,
  });
};
