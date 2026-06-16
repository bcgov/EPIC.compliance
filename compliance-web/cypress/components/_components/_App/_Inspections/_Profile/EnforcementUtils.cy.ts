/// <reference types="cypress" />
import {
  getRequirementDeleteWarning,
  hasCreatedEnforcementAction,
} from "@/components/App/Inspections/Profile/Enforcements/EnforcementUtils";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import {
  defaultRequirementDeleteWarning,
  EnforcementActionEnum,
  hasLinkedEnforcementDeleteWarning,
} from "@/utils/constants";

// Build a minimal requirement marked for the given enforcement action types.
const buildRequirement = (
  id: number,
  markedFor: EnforcementActionEnum[]
): InspectionRequirement =>
  ({
    id,
    enforcement_action_data: markedFor.map((type) => ({
      id: type,
      name: type,
    })),
  }) as unknown as InspectionRequirement;

describe("EnforcementUtils - requirement delete warning", () => {
  describe("getRequirementDeleteWarning", () => {
    it("shows the linked-enforcement warning when an Order has been created", () => {
      const requirement = buildRequirement(1, [EnforcementActionEnum.ORDER]);

      const warning = getRequirementDeleteWarning(requirement, [
        {
          enforcementActionType: EnforcementActionEnum.ORDER,
          // An order exists linked to this requirement.
          reqIds: [[1]],
        },
      ]);

      expect(warning).to.equal(hasLinkedEnforcementDeleteWarning);
    });

    it("shows the default warning when marked for an Order but none created yet", () => {
      const requirement = buildRequirement(1, [EnforcementActionEnum.ORDER]);

      const warning = getRequirementDeleteWarning(requirement, [
        {
          enforcementActionType: EnforcementActionEnum.ORDER,
          // No orders created yet for this inspection.
          reqIds: [],
        },
      ]);

      expect(warning).to.equal(defaultRequirementDeleteWarning);
    });

    it("shows the linked-enforcement warning for a created Warning Letter", () => {
      const requirement = buildRequirement(2, [
        EnforcementActionEnum.WARNING_LETTER,
      ]);

      const warning = getRequirementDeleteWarning(requirement, [
        {
          enforcementActionType: EnforcementActionEnum.WARNING_LETTER,
          reqIds: [[2]],
        },
      ]);

      expect(warning).to.equal(hasLinkedEnforcementDeleteWarning);
    });

    it("shows the linked-enforcement warning for a created Administrative Penalty", () => {
      const requirement = buildRequirement(3, [
        EnforcementActionEnum.AP_RECOMMENDATION,
      ]);

      const warning = getRequirementDeleteWarning(requirement, [
        {
          enforcementActionType: EnforcementActionEnum.AP_RECOMMENDATION,
          reqIds: [[3]],
        },
      ]);

      expect(warning).to.equal(hasLinkedEnforcementDeleteWarning);
    });

    it("shows the default warning when a different requirement owns the created enforcement", () => {
      const requirement = buildRequirement(1, [EnforcementActionEnum.ORDER]);

      const warning = getRequirementDeleteWarning(requirement, [
        {
          enforcementActionType: EnforcementActionEnum.ORDER,
          // The order is linked to requirement 99, not requirement 1.
          reqIds: [[99]],
        },
      ]);

      expect(warning).to.equal(defaultRequirementDeleteWarning);
    });

    it("shows the default warning when the requirement is not marked for any enforcement", () => {
      const requirement = buildRequirement(1, []);

      const warning = getRequirementDeleteWarning(requirement, [
        {
          enforcementActionType: EnforcementActionEnum.ORDER,
          reqIds: [[1]],
        },
      ]);

      expect(warning).to.equal(defaultRequirementDeleteWarning);
    });

    it("shows the default warning when there is no requirement", () => {
      const warning = getRequirementDeleteWarning(undefined, [
        {
          enforcementActionType: EnforcementActionEnum.ORDER,
          reqIds: [[1]],
        },
      ]);

      expect(warning).to.equal(defaultRequirementDeleteWarning);
    });
  });

  describe("hasCreatedEnforcementAction", () => {
    it("is true when the requirement is in a created enforcement's requirement map", () => {
      const requirement = buildRequirement(5, [EnforcementActionEnum.ORDER]);

      expect(
        hasCreatedEnforcementAction(requirement, [
          { enforcementActionType: EnforcementActionEnum.ORDER, reqIds: [[5]] },
        ])
      ).to.equal(true);
    });

    it("is false when marked for the type but no enforcement record exists", () => {
      const requirement = buildRequirement(5, [EnforcementActionEnum.ORDER]);

      expect(
        hasCreatedEnforcementAction(requirement, [
          { enforcementActionType: EnforcementActionEnum.ORDER, reqIds: [] },
        ])
      ).to.equal(false);
    });

    it("checks each enforcement type and returns true if any has a created record", () => {
      const requirement = buildRequirement(7, [
        EnforcementActionEnum.ORDER,
        EnforcementActionEnum.WARNING_LETTER,
      ]);

      expect(
        hasCreatedEnforcementAction(requirement, [
          // No order created for it...
          { enforcementActionType: EnforcementActionEnum.ORDER, reqIds: [] },
          // ...but a warning letter has been.
          {
            enforcementActionType: EnforcementActionEnum.WARNING_LETTER,
            reqIds: [[7]],
          },
        ])
      ).to.equal(true);
    });
  });
});
