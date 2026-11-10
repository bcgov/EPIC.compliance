import { describe, expect, it } from "vitest";
import { hasActiveFilters, isFilterValueActive } from "./filterUtils";

describe("isFilterValueActive", () => {
  it.each([
    [undefined, false],
    [null, false],
    ["", false],
    ["   ", false],
    [[], false],
    ["2026-01-01", true],
    [["Open"], true],
    [0, true],
  ])("%j -> %s", (value, expected) => {
    expect(isFilterValueActive(value)).toBe(expected);
  });
});

describe("hasActiveFilters", () => {
  it("is false with no filters", () => {
    expect(hasActiveFilters([])).toBe(false);
    expect(hasActiveFilters([], {})).toBe(false);
  });

  it("is false when every filter has been cleared to an empty value", () => {
    expect(
      hasActiveFilters(
        [
          { id: "status", value: [] },
          { id: "date_created", value: "" },
        ],
        { primary_officer_ids: [], globalFilter: "" }
      )
    ).toBe(false);
  });

  it("is true for a default column filter such as Status = Open", () => {
    expect(hasActiveFilters([{ id: "status", value: ["Open"] }])).toBe(true);
  });

  it("is true for an external filter alone", () => {
    expect(hasActiveFilters([], { primary_officer_ids: ["7"] })).toBe(true);
  });
});
