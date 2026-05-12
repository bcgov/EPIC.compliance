import {
  Complaint,
  ComplaintAPIData,
  ComplaintGridItems,
  ComplaintGridQueryParams,
  ComplaintStatusAPIData,
} from "@/models/Complaint";
import { ComplaintSource } from "@/models/ComplaintSource";
import { Contact } from "@/models/Contact";
import {
  RequirementDetails,
  RequirementSource,
} from "@/models/RequirementSource";
import { OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useStaticQuery } from "@/hooks/useCustomQueries";
import { ComplaintResolution } from "@/models/ComplaintResolution";

const fetchRequirementSources = (): Promise<RequirementSource[]> => {
  return request({ url: "/requirement-sources" });
};

const fetchComplaintSources = (): Promise<ComplaintSource[]> => {
  return request({ url: "/complaints/sources" });
};

const fetchComplaintResolutions = (): Promise<ComplaintResolution[]> => {
  return request({ url: "/complaints/resolutions" });
};

const fetchComplaints = (
  queryParams: ComplaintGridQueryParams = {}
): Promise<ComplaintGridItems> => {
  return request({ url: "/complaints", params: queryParams });
};

const complaintsExport = (queryParams: ComplaintGridQueryParams = {}) => {
  delete queryParams.page_no;
  delete queryParams.page_size;
  return request({
    method: "POST",
    url: `/complaints/export`,
    data: queryParams,
    responseType: "blob",
  });
};

const fetchComplaint = (complaintNumber: string): Promise<Complaint> => {
  return request({ url: `/complaints/complaint-numbers/${complaintNumber}` });
};

const fetchSourceContact = (complaintId: number): Promise<Contact> => {
  return request({ url: `/complaints/${complaintId}/source-contacts` });
};

const fetchRequirementDetails = (
  complaintId: number
): Promise<RequirementDetails> => {
  return request({ url: `/complaints/${complaintId}/requirement-details` });
};

const createComplaint = (complaint: ComplaintAPIData) => {
  return request({ url: "/complaints", method: "post", data: complaint });
};

const updateComplaint = ({
  id,
  complaint,
}: {
  id: number;
  complaint: ComplaintAPIData;
}) => {
  return request({
    url: `/complaints/${id}`,
    method: "patch",
    data: complaint,
  });
};

const updateComplaintStatus = ({
  id,
  complaintStatus,
}: {
  id: number;
  complaintStatus: ComplaintStatusAPIData;
}) => {
  return request({
    url: `/complaints/${id}/status`,
    method: "patch",
    data: complaintStatus,
  });
};

const deleteComplaint = (id: number) => {
  return request({ url: `/complaints/${id}`, method: "delete" });
};

export const useRequirementSourcesData = () => {
  return useStaticQuery({
    queryKey: ["requirement-sources"],
    queryFn: fetchRequirementSources,
  });
};

export const useComplaintSourcesData = () => {
  return useStaticQuery({
    queryKey: ["complaint-sources"],
    queryFn: fetchComplaintSources,
  });
};

export const useComplaintResolutionsData = () => {
  return useStaticQuery({
    queryKey: ["complaint-resolutions"],
    queryFn: fetchComplaintResolutions,
  });
};

export const useComplaintsData = (
  queryParams: ComplaintGridQueryParams = {}
) => {
  return useQuery({
    queryKey: ["complaints", queryParams],
    queryFn: () => fetchComplaints(queryParams),
  });
};

export const useComplaintsExport = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: complaintsExport, onSuccess });
};

export const useComplaintsByCaseFileId = (caseFileId: number) => {
  return useQuery({
    queryKey: ["complaints-by-caseFileId", caseFileId],
    queryFn: () => fetchComplaints({ case_file_id: caseFileId.toString() }),
    enabled: !!caseFileId,
  });
};

export const useComplaintByNumber = (complaintNumber: string) => {
  return useQuery({
    queryKey: ["complaint", complaintNumber],
    queryFn: async () => {
      const complaint = await fetchComplaint(complaintNumber);
      const [source_contact, requirement_detail] = await Promise.all([
        fetchSourceContact(complaint?.id),
        fetchRequirementDetails(complaint?.id),
      ]);
      return { ...complaint, source_contact, requirement_detail };
    },
    enabled: !!complaintNumber,
  });
};

export const useCreateComplaint = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createComplaint, onSuccess });
};

export const useUpdateComplaint = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateComplaint, onSuccess });
};

export const useUpdateComplaintStatus = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: updateComplaintStatus, onSuccess });
};

export const useDeleteComplaint = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: deleteComplaint, onSuccess });
};
