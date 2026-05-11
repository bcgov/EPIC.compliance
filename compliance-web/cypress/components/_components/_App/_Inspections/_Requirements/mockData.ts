import { Inspection } from "@/models/Inspection";
import { InspectionRequirement } from "@/models/InspectionRequirement";


export const baseRequirement: InspectionRequirement = {
  id: 1,
  inspection_id: 100,
  summary: "Test Requirement",
  topic: { id: 1, name: "Test Topic" },
  topic_id: 1,
  agency_id: 1,
  enforcement_action_id: 1,
  compliance_finding_id: 1,
  findings: "Test Findings",
  sort_order: 1,
  is_active: true,
  requirement_source_details: [
    {
      requirement_source: { id: "1", name: "Test Source", source_title: "Test Source Title" },
      requirement_source_id: 1,
      section_number: "1.1",
      condition_number: null,
      amendment_number: "1",
      title: "Test Title",
      description: "Test Description",
      is_active: true,
      id: 1,
      requirement_id: 1,
      source_title: "Test Source Title",
      appendix_id: 1,
      appendix: { id: 1, appendix_no: "A", document_title: "Test Document Title", inspection_id: 1 },
      images: [],
      order_id: 1,
      order: { id: 1, order_number: "1", inspection_id: 1, where_as: "Test Where As", now_therefore: "Test Now Therefore", is_active: true },
      documents: [
        {
          id: 1, req_detail_id: 1, document_type: { id: "1", name: "Test Document" },
          document_type_id: 1,
          document_title: "Test Document",
          section_number: "1.1",
          section_title: "Test Section",
          description: "Test Description",
          is_active: true,
          appendix: { id: 1, appendix_no: "A", document_title: "Test Document Title", inspection_id: 1 },
          appendix_id: 1,
          images: [],
        },
      ],
    },
  ],
  compliance_finding: { id: "1", name: "Out" },
  enforcement_action_data: [{ id: "1", name: "No Action Required" }],
  req_type: { id: "REQ", name: "Requirement" },
  agency: { id: 1, name: "Test Agency" },
};


export const regulatoryRequirement: InspectionRequirement = {
  ...baseRequirement,
  req_type: { id: "REG", name: "Regulatory Considerations" },
};

export const mockInspection: Inspection = {
  id: 1,
  ir_number: "IR123",
  case_file_id: 1,
  project_id: 1,
  location_description: "Test Location",
  utm: "1234567890",
  initiation_id: 1,
  ir_status_id: 1,
  project_status_id: 1,
  is_active: true,
  primary_officer_id: 1,
  start_date: "2021-01-01",
  end_date: "2021-01-01",
  types: [],
  types_text: "",
  inspection_status: "",
  primary_officer: null,
  ir_status: null,
  case_file: null,
  project_status: null,
  project: null,
  initiation: null,
  debrief_date: "2021-01-01",
};
