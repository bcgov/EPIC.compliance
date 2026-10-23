import { describe, expect, it } from "vitest";
import { formatRequirementSources } from "./EnforcementUtils";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { AdministrativePenalty } from "@/models/AdministrativePenalty";
import { InspectionOrder } from "@/models/InspectionOrder";
import { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import { ChargeRecommendation } from "@/models/ChargeRecommendation";
import { ViolationTicket } from "@/models/ViolationTicket";
import { RestorativeJustice } from "@/models/RestorativeJustice";

const SOURCES = {
  EC_CERTIFICATE: { id: 3, name: "EC Certificate", sort_order: 2 },
  EC_AMENDMENT: { id: 10, name: "EC Amendment", sort_order: 3 },
  SCHEDULE_B: { id: 1, name: "Schedule B", sort_order: 5 },
};

const buildRequirement = (
  id: number,
  source: (typeof SOURCES)[keyof typeof SOURCES],
  conditionNumber: string
): InspectionRequirement =>
  ({
    id,
    requirement_source_details: [
      {
        requirement_source_id: source.id,
        requirement_source: source,
        condition_number: conditionNumber,
      },
    ],
  }) as unknown as InspectionRequirement;

const linkedRequirements = [
  buildRequirement(1, SOURCES.SCHEDULE_B, "77"),
  buildRequirement(2, SOURCES.EC_AMENDMENT, "12"),
  buildRequirement(3, SOURCES.SCHEDULE_B, "17"),
  buildRequirement(4, SOURCES.SCHEDULE_B, "1"),
  buildRequirement(5, SOURCES.EC_CERTIFICATE, "1"),
];

const toMaps = (requirements: InspectionRequirement[]) =>
  requirements.map((inspection_requirement) => ({ inspection_requirement }));

const EXPECTED = [
  "EC Certificate, #1",
  "EC Amendment, #12",
  "Schedule B, #1, #17, #77",
];

describe("formatRequirementSources ordering (COMP-953)", () => {
  const maps = toMaps(linkedRequirements);

  const callFor: Record<string, () => string[]> = {
    "Administrative Penalty": () =>
      formatRequirementSources([], undefined, undefined, {
        administrative_penalty_requirement_maps: maps,
      } as unknown as AdministrativePenalty),
    Order: () =>
      formatRequirementSources([], {
        order_requirement_maps: maps,
      } as unknown as InspectionOrder),
    "Warning Letter": () =>
      formatRequirementSources([], undefined, {
        warning_letter_requirement_maps: maps,
      } as unknown as InspectionWarningLetter),
    "Charge Recommendation": () =>
      formatRequirementSources([], undefined, undefined, undefined, {
        charge_recommendation_requirement_maps: maps,
      } as unknown as ChargeRecommendation),
    "Violation Ticket": () =>
      formatRequirementSources([], undefined, undefined, undefined, undefined, {
        violation_ticket_requirement_maps: maps,
      } as unknown as ViolationTicket),
    "Restorative Justice": () =>
      formatRequirementSources([], undefined, undefined, undefined, undefined, undefined, {
        restorative_justice_requirement_maps: maps,
      } as unknown as RestorativeJustice),
  };

  it.each(Object.keys(callFor))(
    "sorts sources by dropdown order and conditions numerically for %s",
    (label) => {
      expect(callFor[label]()).toEqual(EXPECTED);
    }
  );

  it("does not depend on the order requirements were linked", () => {
    const reversed = toMaps([...linkedRequirements].reverse());
    const result = formatRequirementSources([], undefined, undefined, {
      administrative_penalty_requirement_maps: reversed,
    } as unknown as AdministrativePenalty);
    expect(result).toEqual(EXPECTED);
  });

  it("sorts condition numbers numerically, not as text", () => {
    const result = formatRequirementSources([], undefined, undefined, {
      administrative_penalty_requirement_maps: toMaps([
        buildRequirement(1, SOURCES.SCHEDULE_B, "9"),
        buildRequirement(2, SOURCES.SCHEDULE_B, "10"),
        buildRequirement(3, SOURCES.SCHEDULE_B, "2"),
      ]),
    } as unknown as AdministrativePenalty);
    expect(result).toEqual(["Schedule B, #2, #9, #10"]);
  });

  it("shows a condition number once when several requirements cite it", () => {
    const result = formatRequirementSources([], undefined, undefined, {
      administrative_penalty_requirement_maps: toMaps([
        buildRequirement(1, SOURCES.SCHEDULE_B, "5"),
        buildRequirement(2, SOURCES.SCHEDULE_B, "5"),
        buildRequirement(3, SOURCES.SCHEDULE_B, " 5 "),
      ]),
    } as unknown as AdministrativePenalty);
    expect(result).toEqual(["Schedule B, #5"]);
  });
});
