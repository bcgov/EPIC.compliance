import { ComplianceFinding } from "@/models/ComplianceFinding";
import { RequirementDocumentType } from "@/models/RequirementDocumentType";
import { EnforcementAction } from "@/models/EnforcementAction";
import { OnSuccessType, request } from "@/utils/axiosUtils";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  InspectionRequirement,
  InspectionRequirementAPIData,
  InspectionRequirementBatchAPIData,
} from "@/models/InspectionRequirement";
import { InspectionRequirementType } from "@/models/InspectionRequirementType";
import { RequirementImage } from "@/models/Image";
import { useStaticQuery } from "./useCustomQueries";

const fetchInspectionRequirementTypes = (): Promise<
  InspectionRequirementType[]
> => {
  return request({ url: "/inspection-requirement-types" });
};

const fetchEnforcementActions = (): Promise<EnforcementAction[]> => {
  return request({ url: "/enforcement-actions" });
};

const fetchComplianceFindings = (): Promise<ComplianceFinding[]> => {
  return request({ url: "/compliance-findings" });
};

const fetchDocumentTypes = (): Promise<RequirementDocumentType[]> => {
  return request({ url: "/document-types" });
};

const fetchInspectionRequirements = (
  inspectionId: number
): Promise<InspectionRequirement[]> => {
  return request({ url: `/inspections/${inspectionId}/requirements` });
};

const fetchInspectionRequirementImages = (
  inspectionId: number
): Promise<RequirementImage[]> => {
  return request({
    url: `/inspections/${inspectionId}/images`,
  });
};

const fetchRequirementSourceImages = (
  inspectionId: number,
  requirementId: number
): Promise<RequirementImage[]> => {
  return request({
    url: `/inspections/${inspectionId}/requirements/${requirementId}/requirement-source-images`,
  });
};

const fetchRequirementDocumentImages = (
  inspectionId: number,
  requirementId: number
): Promise<RequirementImage[]> => {
  return request({
    url: `/inspections/${inspectionId}/requirements/${requirementId}/requirement-document-images`,
  });
};

const createInspectionRequirement = ({
  inspectionId,
  inspectionRequirement,
}: {
  inspectionId: number;
  inspectionRequirement: InspectionRequirementAPIData;
}) => {
  return request({
    url: `/inspections/${inspectionId}/requirements`,
    method: "post",
    data: inspectionRequirement,
  });
};

const updateInspectionRequirement = ({
  inspectionId,
  requirementId,
  inspectionRequirement,
}: {
  inspectionId: number;
  requirementId: number;
  inspectionRequirement: InspectionRequirementAPIData;
  requirementBatch?: InspectionRequirementBatchAPIData[];
}) => {
  return request({
    url: `/inspections/${inspectionId}/requirements/${requirementId}`,
    method: "patch",
    data: inspectionRequirement,
  });
};

const updateInspectionRequirementOrder = ({
  inspectionId,
  requirementId,
  sortOrder,
}: {
  inspectionId: number;
  requirementId: number;
  sortOrder: number;
}) => {
  return request({
    url: `/inspections/${inspectionId}/requirements/${requirementId}/sort-order`,
    method: "patch",
    data: {
      order: sortOrder,
    },
  });
};

const updateInspectionRequirementBatch = ({
  inspectionId,
  requirementBatch,
}: {
  inspectionId: number;
  requirementBatch: InspectionRequirementBatchAPIData[];
}) => {
  return request({
    url: `/inspections/${inspectionId}/requirements`,
    method: "patch",
    data: {
      requirements: requirementBatch,
    },
  });
};

const deleteInspectionRequirement = ({
  inspectionId,
  requirementId,
}: {
  inspectionId: number;
  requirementId: number;
  requirementBatch?: InspectionRequirementBatchAPIData[];
}) => {
  return request({
    url: `/inspections/${inspectionId}/requirements/${requirementId}`,
    method: "delete",
  });
};

export const useInspectionRequirementTypesData = () => {
  return useStaticQuery({
    queryKey: ["inspection-requirement-types"],
    queryFn: fetchInspectionRequirementTypes,
  });
};

export const useEnforcementActionsData = () => {
  return useStaticQuery({
    queryKey: ["enforcement-actions"],
    queryFn: fetchEnforcementActions,
  });
};

export const useComplianceFindingsData = () => {
  return useStaticQuery({
    queryKey: ["compliance-findings"],
    queryFn: fetchComplianceFindings,
  });
};

export const useDocumentTypesData = () => {
  return useStaticQuery({
    queryKey: ["document-types"],
    queryFn: fetchDocumentTypes,
  });
};

export const useInspectionRequirementsData = (inspectionId: number) => {
  return useQuery({
    queryKey: ["inspection-requirements", inspectionId],
    queryFn: () => fetchInspectionRequirements(inspectionId),
    enabled: !!inspectionId,
    staleTime: Infinity,
  });
};

export const useInspectionRequirementImages = (inspectionId: number) => {
  return useQuery({
    queryKey: ["inspection-requirement-images", inspectionId],
    queryFn: () => fetchInspectionRequirementImages(inspectionId),
    select: (data: RequirementImage[]) => {
      const reqPhotos = data
        .filter((image) => image.image_type?.toLowerCase() === "photo")
        .map((image) => ({
          ...image,
          dbId: image.id,
        }));
      const reqFigures = data
        .filter((image) => image.image_type?.toLowerCase() === "figure")
        .map((image) => ({
          ...image,
          dbId: image.id,
        }));
      return {
        photos: reqPhotos,
        figures: reqFigures,
      };
    },
    enabled: !!inspectionId,
    refetchOnWindowFocus: false,
    staleTime: Infinity,
  });
};

export const useRequirementSourceImages = (
  inspectionId: number,
  requirementId: number,
  staleTime: number = Infinity
) => {
  return useQuery({
    queryKey: ["requirement-source-images", inspectionId, requirementId],
    queryFn: () => fetchRequirementSourceImages(inspectionId, requirementId),
    select: (data: RequirementImage[]) => {
      return data.map((image) => ({
        ...image,
        dbId: image.id,
      }));
    },
    enabled: !!inspectionId && !!requirementId,
    refetchOnWindowFocus: false,
    staleTime: staleTime,
  });
};

export const useRequirementDocumentImages = (
  inspectionId: number,
  requirementId: number,
  staleTime: number = Infinity
) => {
  return useQuery({
    queryKey: ["requirement-document-images", inspectionId, requirementId],
    queryFn: () => fetchRequirementDocumentImages(inspectionId, requirementId),
    select: (data: RequirementImage[]) => {
      return data.map((image) => ({
        ...image,
        dbId: image.id,
      }));
    },
    enabled: !!inspectionId && !!requirementId,
    refetchOnWindowFocus: false,
    staleTime: staleTime,
  });
};

export const useCreateInspectionRequirement = (onSuccess: OnSuccessType) => {
  return useMutation({ mutationFn: createInspectionRequirement, onSuccess });
};

export const useUpdateInspectionRequirement = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: updateInspectionRequirement,
    onSuccess(data, variables) {
      // Batch update the requirement findings & images
      if (variables.requirementBatch) {
        updateInspectionRequirementBatch({
          inspectionId: variables.inspectionId,
          requirementBatch: variables.requirementBatch,
        });
      }
      onSuccess(data);
    },
  });
};

export const useUpdateInspectionRequirementOrder = (
  onSuccess: OnSuccessType
) => {
  return useMutation({
    mutationFn: updateInspectionRequirementOrder,
    onSuccess,
  });
};

export const useDeleteInspectionRequirement = (onSuccess: OnSuccessType) => {
  return useMutation({
    mutationFn: deleteInspectionRequirement,
    onSuccess(data, variables) {
      // Batch update the requirement findings & images
      if (variables.requirementBatch) {
        updateInspectionRequirementBatch({
          inspectionId: variables.inspectionId,
          requirementBatch: variables.requirementBatch,
        });
      }
      onSuccess(data);
    },
  });
};

export const useUpdateInspectionRequirementBatch = (
  onSuccess: OnSuccessType
) => {
  return useMutation({
    mutationFn: updateInspectionRequirementBatch,
    onSuccess,
  });
};
