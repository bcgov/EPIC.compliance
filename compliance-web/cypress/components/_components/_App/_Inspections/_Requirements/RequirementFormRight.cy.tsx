import RequirementFormRight from "@/components/App/Inspections/Profile/Requirements/RequirementFormRight";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import { CaseFile } from "@/models/CaseFile";
import { RequirementSourceFormData } from "@/models/InspectionRequirementSource";
import { RequirementSourceEnum } from "@/utils/constants";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

const mockCaseFile: CaseFile = {
  id: 1,
  project_id: 0,
  date_created: "",
  primary_officer_id: 0,
  case_file_number: "123",
  case_file_status: "open",
  initiation: undefined,
  is_active: false,
  project: undefined,
  primary_officer: undefined
};

const mountComponent = (reqSrcList: RequirementSourceFormData[]) => {
  const mockOnDataChange = cy.stub().as("onDataChange");

  cy.mount(
    <QueryClientProvider client={queryClient}>
      <ModalProvider />
      <RequirementFormRight
        onDataChange={mockOnDataChange}
        requirementSourceFormDataList={reqSrcList}
        inspectionId={1}
        caseFile={mockCaseFile}
        requirementId={1}
        isRegulatoryConsideration={false}
        isRequirementEditable={true}
      />
    </QueryClientProvider>
  );
};

describe("RequirementFormRight Component", () => {
  const mockInitialData: RequirementSourceFormData[] = [
    {
      id: 1,
      conditionNumber: "1.1",
      title: "Test Requirement",
      requirementSource: {
        id: RequirementSourceEnum.EAC,
        name: "EAC Certificate",
        source_title: "EAC# M19-01",
      },
      relatedDocuments: [],
    },
  ];

  beforeEach(() => {
    mountComponent(mockInitialData);
  });

  it("renders the component with initial data", () => {
    cy.contains("button", "Requirement Source").should("exist");
    cy.contains("Test Requirement").should("exist");
  });

  it("opens requirement source modal when add button is clicked", () => {
    cy.contains("button", "Requirement Source").click();
    cy.contains("Add Requirement Source").should("exist");

    cy.get('[contenteditable="true"]').type("Test Description");
    cy.contains("button", "Add").should("exist").click();

    cy.get("button[aria-label='close']").should("exist").click();
    cy.contains("Add Requirement Source").should("not.exist");
  });

  it("displays requirement source card with correct data", () => {
    cy.contains(mockInitialData[0].conditionNumber).should("exist");
    cy.contains(mockInitialData[0].title).should("exist");
  });

  it("allows editing a requirement source", () => {
    cy.get("[data-testid='requirement-source-edit-0']").first().click();
    cy.contains("Edit Requirement Source").should("exist");
    cy.get("button[aria-label='close']").should("exist").click();
    cy.contains("Edit Requirement Source").should("not.exist");
  });

  it("shows delete confirmation when trying to delete a requirement source", () => {
    cy.get("[data-testid='requirement-source-delete-0']").first().click();
    cy.contains("Delete Requirement Source?").should("exist");
    cy.contains("button", "Delete").should("exist");
    cy.get("[data-testid='cancel-action-modal-button']")
      .should("exist")
      .click();
    cy.contains("Delete Requirement Source?").should("not.exist");
  });

  it("renders images containers", () => {
    cy.contains("Photos").should("exist");
    cy.contains("Figures").should("exist");
  });

  it("renders appendices container", () => {
    cy.contains("Appendices").should("exist");
  });
});

describe("RequirementFormRight Component with Related Documents", () => {
  const mockDataWithRelatedDocs: RequirementSourceFormData[] = [
    {
      id: 1,
      conditionNumber: "1.1",
      title: "Test Requirement",
      requirementSource: {
        id: RequirementSourceEnum.EAC,
        name: "EAC Certificate",
        source_title: "EAC# M19-01",
      },
      relatedDocuments: [
        {
          id: 1,
          sourceFormId: 1,
          documentTitle: "Related Doc",
          sections: [
            {
              id: 1,
              sourceFormId: 1,
              relatedDocumentFormId: 1,
              sectionNumber: "1.1",
              sectionTitle: "Test Section",
            },
          ],
        },
      ],
    },
  ];

  beforeEach(() => {
    mountComponent(mockDataWithRelatedDocs);
  });

  it("displays related documents", () => {
    cy.contains("Related Doc").should("exist");
  });

  it("displays document sections", () => {
    cy.contains("Test Section").should("exist");
  });

  it("allows adding new document section", () => {
    cy.get(
      "[data-testid='requirement-related-document-add-section-0']"
    ).click();
    cy.contains("Add Section").should("exist");
    cy.get("button[aria-label='close']").should("exist").click();
    cy.contains("Add Section").should("not.exist");
  });

  it("allows editing a document section", () => {
    cy.get("[data-testid='requirement-related-document-edit-0-0']").click();
    cy.contains("Edit Related Document").should("exist");
    cy.get("button[aria-label='close']").should("exist").click();
    cy.contains("Edit Related Document").should("not.exist");
  });

  it("shows delete confirmation when trying to delete a section", () => {
    cy.get("[data-testid='requirement-related-document-delete-0-0']")
      .first()
      .click();
    cy.contains("Delete Section?").should("exist");
    cy.contains("button", "Delete").should("exist");
    cy.get("[data-testid='cancel-action-modal-button']")
      .should("exist")
      .click();
    cy.contains("Delete Section?").should("not.exist");
  });
});
