import RequirementRelatedDocumentModal from "@/components/App/Inspections/Profile/Requirements/RequirementSource/RequirementRelatedDocumentModal";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  RequirementSourceFormData,
  RequirementRelatedDocumentData,
} from "@/models/InspectionRequirementSource";
import {
  RequirementSourceEnum,
  RequirementDocumentTypeEnum,
} from "@/utils/constants";
import { RequirementDocumentType } from "@/models/RequirementDocumentType";

const mockDocumentTypes: RequirementDocumentType[] = [
  { id: RequirementDocumentTypeEnum.OTHER_DOCUMENT, name: "Other Document" },
  { id: RequirementDocumentTypeEnum.MANAGEMENT_PLAN, name: "Management Plan" },
];

const mockSourceData: RequirementSourceFormData = {
  id: 1,
  dbId: 1,
  requirementSource: {
    id: RequirementSourceEnum.SCHEDULE_B,
    name: "Schedule B",
    source_title: "Schedule B",
  },
  conditionNumber: "1.1",
  title: "Test Source",
  description: { html: "<p>Test</p>", text: "Test" },
  relatedDocuments: [],
};

const mockRelatedDocumentData: RequirementRelatedDocumentData = {
  id: 1,
  sourceFormId: 1,
  relatedDocument: mockDocumentTypes[0],
  documentTitle: "Test Document",
  sections: [
    {
      id: 1,
      dbId: 1,
      sourceFormId: 1,
      relatedDocumentFormId: 1,
      sectionNumber: "1.1",
      sectionTitle: "Test Section",
      description: {
        html: "<p>Test Description</p>",
        text: "Test Description",
      },
    },
  ],
};

describe("RequirementRelatedDocumentModal", () => {
  const queryClient = new QueryClient();

  function mountRelatedDocumentModal(args?: {
    relatedDocumentData?: RequirementRelatedDocumentData;
    isEditSection?: boolean;
    relatedDocumentSectionData?: (typeof mockRelatedDocumentData.sections)[0];
  }): React.ReactNode {
    const { relatedDocumentData, isEditSection, relatedDocumentSectionData } =
      args ?? {};

    return (
      <QueryClientProvider client={queryClient}>
        <RequirementRelatedDocumentModal
          onSubmit={cy.stub().as("onSubmit")}
          requirementSourceData={mockSourceData}
          relatedDocumentData={relatedDocumentData}
          relatedDocumentSectionData={relatedDocumentSectionData}
          isEditSection={isEditSection}
        />
      </QueryClientProvider>
    );
  }

  beforeEach(() => {
    // Mock the document types API hook
    cy.stub(window, "fetch").resolves({
      ok: true,
      json: () => Promise.resolve(mockDocumentTypes),
    });
  });

  it("renders add related document form correctly", () => {
    cy.mount(mountRelatedDocumentModal());

    cy.contains("Add Related Document").should("be.visible");
    cy.contains("Related Document").should("exist");
    cy.contains("Document Title").should("exist");
    cy.contains("Section #").should("exist");
    cy.contains("Section Title").should("exist");
    cy.contains("Description").should("be.visible");
    cy.contains("button", "Add").should("be.visible");
  });

  it("renders edit section form correctly", () => {
    cy.mount(
      mountRelatedDocumentModal({
        relatedDocumentData: mockRelatedDocumentData,
        isEditSection: true,
        relatedDocumentSectionData: mockRelatedDocumentData.sections[0],
      })
    );

    cy.contains("Edit Related Document").should("be.visible");
    cy.get('[name="relatedDocument"]').should("be.disabled");
    cy.contains("button", "Save").should("be.visible");
  });

  it("shows source information in the header", () => {
    cy.mount(mountRelatedDocumentModal());

    cy.contains("Schedule B").should("be.visible");
    cy.contains("1.1").should("be.visible");
  });

  it("validates required fields", () => {
    cy.mount(mountRelatedDocumentModal());

    // Try to submit without required fields
    cy.contains("button", "Add").click();
    cy.contains("Description is required").should("be.visible");
  });

  it("submits form with valid data", () => {
    cy.mount(
      mountRelatedDocumentModal({
        relatedDocumentData: mockRelatedDocumentData,
      })
    );

    // Fill out the form
    cy.get('textarea[name="documentTitle"]').clear();
    cy.get('textarea[name="documentTitle"]').type("Test Document");
    cy.get('input[name="sectionNumber"]').type("1.1");
    cy.get('textarea[name="sectionTitle"]').type("Test Section");

    // Type in the Lexical editor
    cy.get('[contenteditable="true"]').type("Test Description");

    // Submit the form
    cy.contains("button", "Add").click();

    // Verify submission
    cy.get("@onSubmit").should("be.calledOnce");
  });
});
