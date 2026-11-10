import { describe, expect, it } from "vitest";
import dateUtils from "@/utils/dateUtils";
import { formatInspectionDateRange } from "./InspectionFormUtils";

const start = "2024-08-28T20:18:55.740Z";
const end = "2024-08-30T20:18:55.741Z";

describe("formatInspectionDateRange", () => {
  it("shows start date only when end date is missing", () => {
    expect(formatInspectionDateRange(start, null)).toBe(dateUtils.formatDate(start));
    expect(formatInspectionDateRange(start, undefined)).toBe(dateUtils.formatDate(start));
  });

  it("shows start date only when end date is the same day", () => {
    expect(formatInspectionDateRange(start, start)).toBe(dateUtils.formatDate(start));
  });

  it("shows a range when end date differs", () => {
    expect(formatInspectionDateRange(start, end)).toBe(
      `${dateUtils.formatDate(start)} — ${dateUtils.formatDate(end)}`
    );
  });
});
