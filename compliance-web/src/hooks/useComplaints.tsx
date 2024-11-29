import { Complaint, ComplaintAPIData } from "@/models/Complaint";
import { ComplaintSource } from "@/models/ComplaintSource";
import { Contact } from "@/models/Contact";
import {
  RequirementDetails,
  RequirementSource,
} from "@/models/RequirementSource";
import { OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";

const fetchRequirementSources = (): Promise<RequirementSource[]> => {
  return request({ url: "/requirement-sources" });
};

const fetchComplaintSources = (): Promise<ComplaintSource[]> => {
  return request({ url: "/complaints/sources" });
};

const fetchComplaints = (caseFileId?: number): Promise<Complaint[]> => {
  return request({ url: "/complaints", params: { case_file_id: caseFileId } });
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

export const useRequirementSourcesData = () => {
  return useQuery({
    queryKey: ["requirement-sources"],
    queryFn: fetchRequirementSources,
  });
};

export const useComplaintSourcesData = () => {
  return useQuery({
    queryKey: ["complaint-sources"],
    queryFn: fetchComplaintSources,
  });
};

export const useComplaintsData = () => {
  return useQuery({
    queryKey: ["complaints"],
    queryFn: () => fetchComplaints(),
  });
};

export const useComplaintsByCaseFileId = (caseFileId: number) => {
  return useQuery({
    queryKey: ["complaints-by-caseFileId", caseFileId],
    queryFn: () => fetchComplaints(caseFileId),
    enabled: !!caseFileId,
  });
};

export const useComplaintByNumber = (complaintNumber: string) => {
  return useQuery({
    queryKey: ["complaint", complaintNumber],
    queryFn: async () => {
      const complaint = await fetchComplaint(complaintNumber);
      const source_contact = await fetchSourceContact(complaint?.id);
      const requirement_detail = await fetchRequirementDetails(complaint?.id);
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
