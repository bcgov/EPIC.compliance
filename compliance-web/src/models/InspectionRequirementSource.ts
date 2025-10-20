import { Appendix } from "./Appendix";
import { RequirementImage } from "./Image";
import { InspectionOrder } from "./InspectionOrder";
import { RequirementDocumentType } from "./RequirementDocumentType";
import { RequirementSource } from "./RequirementSource";

export interface InspectionRequirementSource {
  id: number,
  requirement_id: number,
  requirement_source_id: number,
  requirement_source: RequirementSource,
  section_number: string,
  condition_number: string,
  amendment_number?: string,
  clause_number?: string,
  regulation_number?: string,
  compliance_number?: string,
  source_title: string,
  appendix_id: number,
  appendix: Appendix,
  order_id: number,
  order: InspectionOrder,
  title: string,
  description: string,
  is_active: boolean,
  documents: InspectionRequirementSourceDocument[],
  images: RequirementImage[],
}

export interface InspectionRequirementSourceDocument {
  id: number,
  req_detail_id: number,
  document_type: RequirementDocumentType,
  document_type_id: number,
  document_title: string,
  section_number: string,
  section_title: string,
  appendix_id: number,
  appendix: Appendix,
  description: string,
  is_active: boolean,
  images: RequirementImage[],
}

export interface RequirementSourceFormData {
  id?: number;
  dbId?: number;
  requirementSource?: RequirementSource;
  requirementSourceTitle?: string;
  regulationNumber?: string;
  exemptionOrderNumber?: string;
  complianceNumber?: string;
  amendmentNumber?: string;
  appendix?: Appendix;
  conditionNumber?: string;
  sectionNumber?: string;
  clauseNumber?: string;
  title?: string,
  order?: InspectionOrder,
  description?: {
    html: string;
    text: string;
  },
  relatedDocuments?: RequirementRelatedDocumentData[];
  images?: RequirementImage[];
}

export interface RequirementRelatedDocumentData {
  id?: number;
  sourceFormId?: number;
  relatedDocument?: RequirementDocumentType;
  documentTitle?: string;
  sections?: RequirementRelatedDocumentSectionData[];
  appendix?: Appendix;
}

export interface RequirementRelatedDocumentSectionData {
  id?: number;
  dbId?: number;
  sourceFormId?: number;
  relatedDocumentFormId?: number;
  appendix?: Appendix;
  sectionNumber?: string;
  sectionTitle?: string;
  description?: {
    html: string;
    text: string;
  };
  images?: RequirementImage[];
}

export interface RequirementRelatedDocumentSectionFormData {
  id?: number;
  relatedDocument?: RequirementDocumentType,
  appendix?: Appendix;
  documentTitle?: string,
  sectionNumber?: string,
  sectionTitle?: string,
  description?: {
    html: string;
    text: string;
  },
}

export interface InspectionRequirementSourceAPIData {
  id?: number,
  requirement_source_id: string,
  source_title?: string,
  section_number?: string,
  condition_number?: string,
  amendment_number?: string,
  regulation_number?: string,
  clause_number?: string,
  compliance_number?: string,
  appendix_id?: number,
  order_id?: number,
  title: string,
  description: string,
  documents: InspectionRequirementSourceDocumentAPIData[],
  images: RequirementImage[],
}

export interface InspectionRequirementSourceDocumentAPIData {
  id?: number,
  document_type_id: string,
  document_title: string,
  section_number: string,
  section_title: string,
  description: string,
  appendix_id?: number,
  images: RequirementImage[],
}
