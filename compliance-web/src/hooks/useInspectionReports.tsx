import { InspectionRecord } from "@/models/InspectionRecord";
import {
  InspectionRecordApprovalPayload,
  IRApproval,
} from "@/models/IRApproval";
import { OnErrorType, OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";

const fetchInspectionReports = (
  inspectionId: number
): Promise<InspectionRecord> => {
  return request({ url: `/inspections/${inspectionId}/inspection-records` });
};

const createInspectionRecord = ({
  inspectionId,
  inspectionRecordType,
}: {
  inspectionId: number;
  inspectionRecordType: {
    ir_status: number;
  };
}) => {
  return request({
    url: `/inspections/${inspectionId}/inspection-records`,
    method: "post",
    data: inspectionRecordType,
  });
};

const updateInspectionRecord = ({
  inspectionId,
  inspectionRecordId,
  updateRecord,
}: {
  inspectionId: number;
  inspectionRecordId: number;
  updateRecord: {
    field_name: string;
    value: string;
  };
}) => {
  return request({
    url: `/inspections/${inspectionId}/inspection-records/${inspectionRecordId}`,
    method: "patch",
    data: updateRecord,
  });
};

const resetInspectionRecord = ({
  inspectionId,
  inspectionRecordId,
  resetPayload,
}: {
  inspectionId: number;
  inspectionRecordId: number;
  resetPayload: {
    field_name: string;
  };
}) => {
  return request({
    url: `/inspections/${inspectionId}/inspection-records/${inspectionRecordId}/reset`,
    method: "patch",
    data: resetPayload,
  });
};

const createIRApproval = ({
  inspectionId,
  inspectionRecordId,
  approvalPayload,
}: {
  inspectionId: number;
  inspectionRecordId: number;
  approvalPayload: {
    approved_by_id?: number;
  };
}) => {
  return request({
    url: `/inspections/${inspectionId}/inspection-records/${inspectionRecordId}/approvals`,
    method: "post",
    data: approvalPayload,
  });
};

const fetchIRApprovals = ({
  inspectionId,
  inspectionRecordId,
}: {
  inspectionId: number;
  inspectionRecordId: number;
}): Promise<IRApproval[]> => {
  return request({
    url: `/inspections/${inspectionId}/inspection-records/${inspectionRecordId}/approvals`,
  });
};

const updateIRApproval = ({
  inspectionId,
  inspectionRecordId,
  approvalId,
  approvalPayload,
}: {
  inspectionId: number;
  inspectionRecordId: number;
  approvalId: number;
  approvalPayload: InspectionRecordApprovalPayload;
}) => {
  return request({
    url: `/inspections/${inspectionId}/inspection-records/${inspectionRecordId}/approvals/${approvalId}`,
    method: "patch",
    data: approvalPayload,
  });
};

const updateIRApprovalStatus = ({
  inspectionId,
  inspectionRecordId,
  approvalId,
  statusPayload,
}: {
  inspectionId: number;
  inspectionRecordId: number;
  approvalId: number;
  statusPayload: {
    approval_status: string;
    approved_by_id: number;
  };
}) => {
  return request({
    url: `/inspections/${inspectionId}/inspection-records/${inspectionRecordId}/approvals/${approvalId}/status`,
    method: "patch",
    data: statusPayload,
  });
};

const updateIRReportToFinal = ({
  inspectionId,
  inspectionRecordId,
}: {
  inspectionId: number;
  inspectionRecordId: number;
}) => {
  return request({
    url: `/inspections/${inspectionId}/inspection-records/${inspectionRecordId}/switch-to-final`,
    method: "patch",
  });
};

const inspectionRecordRender = ({
  inspectionId,
  inspectionRecordId,
  outputFormat,
}: {
  inspectionId: number;
  inspectionRecordId: number;
  outputFormat: "html" | "pdf" | "docx";
}) => {
  return request({
    method: "POST",
    url: `/inspections/${inspectionId}/inspection-records/${inspectionRecordId}/render`,
    data: { output_format: outputFormat },
    responseType: outputFormat === "docx" ? "blob" : "json",
  });
};

const deleteInspectionRecord = ({
  inspectionId,
  inspectionRecordId,
}: {
  inspectionId: number;
  inspectionRecordId: number;
}) => {
  return request({
    url: `/inspections/${inspectionId}/inspection-records/${inspectionRecordId}`,
    method: "delete",
  });
};

export const useInspectionReportsData = (inspectionId?: number) => {
  return useQuery({
    queryKey: ["inspection-reports", inspectionId],
    queryFn: () => fetchInspectionReports(inspectionId!),
    enabled: !!inspectionId,
    refetchInterval: 30000,
  });
};

export const useCreateInspectionRecord = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: createInspectionRecord,
    onSuccess,
  });
};

export const useUpdateInspectionRecord = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: updateInspectionRecord,
    onSuccess,
  });
};

export const useResetInspectionRecord = (onSuccess: OnSuccessType, onError?: OnErrorType) => {
  return useMutation({
    mutationFn: resetInspectionRecord,
    onSuccess,
    onError,
  });
};

export const useCreateIRApproval = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: createIRApproval,
    onSuccess,
  });
};

export const useFetchIRApprovals = (
  inspectionId: number,
  inspectionRecordId: number,
) => {
  return useQuery({
    queryKey: ["ir-approvals", inspectionId, inspectionRecordId],
    queryFn: () => fetchIRApprovals({ inspectionId, inspectionRecordId }),
    enabled: !!inspectionId && !!inspectionRecordId,
    refetchOnMount: true,
    refetchInterval: 30000,
  });
};

export const useUpdateIRApproval = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: updateIRApproval,
    onSuccess,
  });
};

export const useUpdateIRApprovalStatus = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: updateIRApprovalStatus,
    onSuccess,
  });
};

export const useUpdateIRReportToFinal = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: updateIRReportToFinal,
    onSuccess,
  });
};

export const useInspectionRecordRender = (
  onSuccess: OnSuccessType,
  onError?: OnErrorType
) => {
  return useMutation({
    mutationFn: inspectionRecordRender,
    onError,
    onSuccess,
  });
};

export const useDeleteInspectionRecord = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: deleteInspectionRecord,
    onSuccess,
  });
};
