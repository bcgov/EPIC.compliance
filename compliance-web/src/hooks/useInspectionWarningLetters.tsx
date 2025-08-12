import { OnErrorType, OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  InspectionWarningLetter,
  InspectionWarningLetterAPIData,
} from "@/models/InspectionWarningLetter";
import { WarningLetterApproval } from "@/models/WarningLetterApproval";

const fetchWarningLetters = (
  inspectionId: number
): Promise<InspectionWarningLetter[]> => {
  return request({
    url: `/warning-letters`,
    params: { inspection_id: inspectionId },
  });
};

const fetchWarningLetterByNumber = (
  warningLetterNumber: string
): Promise<InspectionWarningLetter[]> => {
  return request({
    url: `/warning-letters/warning-letter-numbers/${warningLetterNumber}`,
  });
};

const createWarningLetter = ({
  inspectionWarningLetter,
}: {
  inspectionWarningLetter: InspectionWarningLetterAPIData;
}) => {
  return request({
    url: `/warning-letters`,
    method: "post",
    data: inspectionWarningLetter,
  });
};

const updateWarningLetter = ({
  inspectionWarningLetterId,
  inspectionWarningLetter,
}: {
  inspectionWarningLetterId: number;
  inspectionWarningLetter: InspectionWarningLetterAPIData;
}) => {
  return request({
    url: `/warning-letters/${inspectionWarningLetterId}`,
    method: "patch",
    data: inspectionWarningLetter,
  });
};

const warningLetterRender = ({
  inspectionWarningLetterId,
  format,
}: {
  inspectionWarningLetterId: number;
  format: "html" | "pdf";
}) => {
  // If requesting PDF, specify responseType as 'blob'
  const responseType = format === "pdf" ? "blob" : "json";

  return request({
    method: "POST",
    url: `/warning-letters/${inspectionWarningLetterId}/render`,
    data: { output_format: format },
    responseType: responseType,
  });
};

const createWarningLetterApproval = ({
  inspectionWarningLetterId,
  approvalPayload,
}: {
  inspectionWarningLetterId: number;
  approvalPayload: {
    approved_by_id?: number;
  };
}) => {
  return request({
    url: `/warning-letters/${inspectionWarningLetterId}/approvals`,
    method: "post",
    data: approvalPayload,
  });
};

const fetchWarningLetterApprovals = ({
  inspectionWarningLetterId,
}: {
  inspectionWarningLetterId: number;
}): Promise<WarningLetterApproval[]> => {
  return request({
    url: `/warning-letters/${inspectionWarningLetterId}/approvals`,
  });
};

const updateWarningLetterApprovalStatus = ({
  inspectionWarningLetterId,
  approvalId,
  statusPayload,
}: {
  inspectionWarningLetterId: number;
  approvalId: number;
  statusPayload: {
    approval_status: string;
    approved_by_id: number;
  };
}) => {
  return request({
    url: `/warning-letters/${inspectionWarningLetterId}/approvals/${approvalId}/status`,
    method: "patch",
    data: statusPayload,
  });
};

const issueWarningLetter = ({
  inspectionWarningLetterId,
  issuePayload,
}: {
  inspectionWarningLetterId: number;
  issuePayload: {
    date_issued: string;
  };
}) => {
  return request({
    url: `/warning-letters/${inspectionWarningLetterId}/issue`,
    method: "patch",
    data: issuePayload,
  });
};

const deleteInspectionWarningLetter = ({
  inspectionWarningLetterId,
}: {
  inspectionWarningLetterId: number;
}) => {
  return request({
    url: `/warning-letters/${inspectionWarningLetterId}`,
    method: "delete",
  });
};

const resetWarningLetterTemplate = ({
  inspectionWarningLetterId,
  fieldName,
}: {
  inspectionWarningLetterId: number;
  fieldName: string;
}) => {
  return request({
    url: `/warning-letters/${inspectionWarningLetterId}/reset`,
    method: "patch",
    data: {
      field_name: fieldName,
    },
  });
};

export const useInspectionWarningLettersData = (
  inspectionId: number,
  { isStaleInfinate = true }: { isStaleInfinate?: boolean } = {}
) => {
  return useQuery({
    queryKey: ["inspection-warning-letters", inspectionId],
    queryFn: () => fetchWarningLetters(inspectionId),
    enabled: !!inspectionId,
    staleTime: isStaleInfinate ? Infinity : 0,
  });
};

export const useFetchWarningLetterByNumber = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: fetchWarningLetterByNumber,
    onSuccess,
  });
};

export const useCreateWarningLetter = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createWarningLetter, onSuccess });
};

export const useUpdateWarningLetter = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateWarningLetter, onSuccess });
};

export const useWarningLetterRendered = (
  onSuccess: OnSuccessType,
  onError: OnErrorType
) => {
  return useMutation({
    mutationFn: warningLetterRender,
    onSuccess,
    onError,
  });
};

export const useCreateWarningLetterApproval = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createWarningLetterApproval, onSuccess });
};

export const useFetchWarningLetterApprovals = (
  inspectionWarningLetterId: number
) => {
  return useQuery({
    queryKey: ["warning-letter-approvals", inspectionWarningLetterId],
    queryFn: () => fetchWarningLetterApprovals({ inspectionWarningLetterId }),
    enabled: !!inspectionWarningLetterId,
    staleTime: Infinity,
  });
};

export const useUpdateWarningLetterApprovalStatus = (
  onSuccess: OnSuccessType
) => {
  return useMutation({
    mutationFn: updateWarningLetterApprovalStatus,
    onSuccess,
  });
};

export const useIssueWarningLetter = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: issueWarningLetter, onSuccess });
};

export const useDeleteWarningLetter = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: deleteInspectionWarningLetter,
    onSuccess,
  });
};

export const useResetWarningLetterTemplate = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: resetWarningLetterTemplate,
    onSuccess,
  });
};
