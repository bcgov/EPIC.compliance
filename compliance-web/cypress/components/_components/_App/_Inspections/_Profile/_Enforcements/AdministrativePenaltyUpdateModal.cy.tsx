/// <reference types="cypress" />
import { mount } from "cypress/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "react-oidc-context";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";
import AdministrativePenaltyUpdateModal from "@/components/App/Inspections/Profile/Enforcements/AdministrativePenalty/AdministrativePenaltyUpdateModal";
import { AdministrativePenalty } from "@/models/AdministrativePenalty";
import { Inspection } from "@/models/Inspection";
import { OidcConfig } from "@/utils/config";

const closedApIssued = {
  id: 1,
  inspection_id: 10,
  administrative_penalty_number: "AP-001",
  date_referred: "2026-01-18T00:00:00.000Z",
  decision_date: "2026-01-18T00:00:00.000Z",
  is_active: true,
  referral_status: { id: "REFERRED_TO_AEO", name: "Referred to AEO" },
  decision: { id: "AP_ISSUED", name: "AP Issued" },
  penalty_amount: "1000.00",
  is_closed: true,
  administrative_penalty_requirement_maps: [],
} as unknown as AdministrativePenalty;

const savedJr = (apFieldsEdited = false) =>
  ({
    ...closedApIssued,
    referral_status: { id: "JUDICIAL_REVIEW", name: "Judicial Review" },
    jr_decision_date: "2026-11-01T00:00:00.000Z",
    is_closed: false,
    is_jr_complete: false,
    jr_ap_fields_edited: apFieldsEdited,
  }) as unknown as AdministrativePenalty;

const inspection = (caseFileStatus: string) =>
  ({
    id: 10,
    case_file: { id: 5, case_file_status: caseFileStatus },
  }) as unknown as Inspection;

// Seeds the OIDC session that useAuth and the API client read.
const login = (username: string, roles: string[] = []) => {
  const encode = (value: object) =>
    btoa(JSON.stringify(value)).replace(/=+$/, "").replace(/\+/g, "-").replace(/\//g, "_");
  const accessToken = [
    encode({ alg: "none" }),
    encode({ resource_access: { [OidcConfig.client_id]: { roles } } }),
    "sig",
  ].join(".");
  sessionStorage.setItem(
    `oidc.user:${OidcConfig.authority}:${OidcConfig.client_id}`,
    JSON.stringify({
      access_token: accessToken,
      token_type: "Bearer",
      profile: { sub: username, preferred_username: username },
      expires_at: Math.floor(Date.now() / 1000) + 3600,
    })
  );
};

const mountModal = (caseFileStatus = "Open", ap = closedApIssued) => {
  mount(
    <QueryClientProvider client={new QueryClient()}>
      <AuthProvider {...OidcConfig}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <AdministrativePenaltyUpdateModal
            administrativePenalty={ap}
            inspectionData={inspection(caseFileStatus)}
            isPrimaryOfficerOrSuperUser
          />
        </LocalizationProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

const selectJrDecision = (name: string) => {
  cy.get('input[placeholder="Select an option..."]').last().click();
  cy.contains("li", name).click();
};

describe("AdministrativePenaltyUpdateModal judicial review", () => {
  beforeEach(() => sessionStorage.clear());

  it("hides the JR checkbox when the case file is closed", () => {
    mountModal("Closed");
    cy.get('[data-testid="jr-checkbox"]').should("not.exist");
  });

  it("asks to proceed, then opens the JR panel with the status locked to Judicial Review", () => {
    mountModal();
    cy.get('[data-testid="jr-checkbox"] input').check();
    cy.contains("Checking this reopens the AP").should("be.visible");
    cy.contains("button", "Proceed").click();
    cy.contains("Checking this reopens the AP").should("not.exist");
    cy.get('input[value="Judicial Review"]').should("be.disabled");
    cy.contains("New Penalty Amount").should("be.visible");
  });

  it("applies the new penalty amount rules per decision", () => {
    mountModal();
    cy.get('[data-testid="jr-checkbox"] input').check();
    cy.contains("button", "Proceed").click();

    selectJrDecision("Reversed");
    cy.get('input[name="jr_new_penalty_amount"]').should("have.value", "0").and("be.disabled");

    selectJrDecision("Upheld");
    cy.get('input[name="jr_new_penalty_amount"]').should("have.value", "1,000").and("be.disabled");

    selectJrDecision("Quashed and Remitted");
    cy.get('input[name="jr_new_penalty_amount"]').should("have.value", "0").and("not.be.disabled");

    selectJrDecision("Substituted");
    cy.get('input[name="jr_new_penalty_amount"]').should("have.value", "0").and("not.be.disabled");
  });

  it("keeps a typed JR amount when a superuser changes the penalty amount", () => {
    login("admin", ["super_user"]);
    mountModal();
    cy.get('[data-testid="jr-checkbox"] input').check();
    cy.contains("button", "Proceed").click();
    selectJrDecision("Substituted");
    cy.get('input[name="jr_new_penalty_amount"]').clear().type("500");
    cy.get('input[name="penalty_amount"]').clear().type("2000");
    cy.get('input[name="jr_new_penalty_amount"]').should("have.value", "500");
  });

  const mountFromLinkedInspection = (
    caseFileStatus: string,
    primaryOfficer: string,
    ap: AdministrativePenalty = closedApIssued
  ) => {
    login("officer");
    cy.intercept("GET", "**/inspections/20", {
      id: 20,
      case_file: { id: 6, case_file_status: caseFileStatus },
      primary_officer: { id: 2, auth_user_guid: primaryOfficer },
    }).as("apInspection");
    mountModal("Open", { ...ap, inspection_id: 20 } as AdministrativePenalty);
    cy.wait("@apInspection");
  };

  it("shows the JR checkbox from a linked inspection to the AP's own primary officer", () => {
    mountFromLinkedInspection("Open", "officer");
    cy.get('[data-testid="jr-checkbox"]').should("exist");
  });

  it("hides the JR checkbox from a linked inspection when the AP's own case file is closed", () => {
    mountFromLinkedInspection("Closed", "officer");
    cy.get('[data-testid="jr-checkbox"]').should("not.exist");
  });

  it("hides the JR checkbox from a linked inspection when not the AP's own primary officer", () => {
    mountFromLinkedInspection("Open", "someone-else");
    cy.get('[data-testid="jr-checkbox"]').should("not.exist");
  });

  it("opens an in-progress JR from a linked inspection read-only unless the AP's own primary officer", () => {
    mountFromLinkedInspection("Open", "someone-else", savedJr());
    cy.get('[data-testid="jr-checkbox"] input').should("be.disabled");
    cy.get('input[name="jr_new_penalty_amount"]').should("be.disabled");

    mountFromLinkedInspection("Open", "officer", savedJr());
    cy.get('[data-testid="jr-checkbox"] input').should("not.be.disabled");
    cy.get('input[name="jr_new_penalty_amount"]').should("not.be.disabled");
  });

  it("resets the form when unchecked before saving", () => {
    mountModal();
    cy.get('[data-testid="jr-checkbox"] input').check();
    cy.contains("button", "Cancel").click();
    cy.get('[data-testid="jr-checkbox"] input').should("not.be.checked");
    cy.contains("Checking this reopens the AP").should("not.exist");
    cy.contains("New Penalty Amount").should("not.exist");
  });

  it("locks the AP fields for a primary officer and discards a saved JR on Yes, Discard", () => {
    mountModal("Open", savedJr());
    cy.get('input[name="penalty_amount"]').should("be.disabled").and("have.value", "1,000");
    cy.contains("button", "Delete").should("not.exist");
    cy.get('[data-testid="jr-checkbox"] input').uncheck();
    cy.contains("restore the AP to its previous closed status").should("be.visible");
    cy.contains("button", "No, Keep").click();
    cy.get('[data-testid="jr-checkbox"] input').should("be.checked");
    cy.contains("New Penalty Amount").should("be.visible");

    cy.get('[data-testid="jr-checkbox"] input').uncheck();
    cy.contains("button", "Yes, Discard").click();
    cy.get('[data-testid="jr-checkbox"] input').should("not.be.checked");
    cy.get('input[value="Referred to AEO"]').should("be.disabled");
    cy.contains("New Penalty Amount").should("not.exist");
    cy.contains("button", "Save").should("be.visible");
  });

  it("warns that AP field changes remain when they were edited during the JR", () => {
    mountModal("Open", savedJr(true));
    cy.get('[data-testid="jr-checkbox"] input').uncheck();
    cy.contains("Changes to other AP fields will remain").should("be.visible");
  });
});
