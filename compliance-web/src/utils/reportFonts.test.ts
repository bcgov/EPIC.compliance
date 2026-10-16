import { describe, expect, it } from "vitest";
import { localizeReportFonts } from "./reportFonts";

const BASE = "https://nrs.objectstore.gov.bc.ca/epic-static-assets/compliance-assets/fonts";

describe("localizeReportFonts", () => {
  it.each([
    ["calibri-regular", "local('Calibri'), local('Calibri-Regular')"],
    ["calibri-italic", "local('Calibri Italic'), local('Calibri-Italic')"],
    ["calibri-bold", "local('Calibri Bold'), local('Calibri-Bold')"],
    ["calibri-bold-italic", "local('Calibri Bold Italic'), local('Calibri-BoldItalic')"],
  ])("rewrites %s.ttf to the locally installed face", (file, expected) => {
    const css = `src: url('${BASE}/${file}.ttf') format('truetype');`;
    expect(localizeReportFonts(css)).toBe(`src: ${expected};`);
  });

  it("handles double-quoted urls", () => {
    const css = `src: url("${BASE}/calibri-bold.ttf") format("truetype");`;
    expect(localizeReportFonts(css)).toBe("src: local('Calibri Bold'), local('Calibri-Bold');");
  });

  it("handles unquoted urls", () => {
    const css = `src: url(${BASE}/calibri-italic.ttf) format('truetype');`;
    expect(localizeReportFonts(css)).toBe("src: local('Calibri Italic'), local('Calibri-Italic');");
  });

  it("rewrites every font-face in the document", () => {
    const css = ["regular", "italic", "bold", "bold-italic"]
      .map((v) => `src: url('${BASE}/calibri-${v}.ttf') format('truetype');`)
      .join("\n");
    const result = localizeReportFonts(css);
    expect(result).not.toContain("objectstore");
    expect(result).not.toContain("url(");
  });

  it("leaves other urls such as logo images untouched", () => {
    const html = `<img src="https://nrs.objectstore.gov.bc.ca/epic-static-assets/compliance-assets/images/BCID_V_RGB_pos.png">`;
    expect(localizeReportFonts(html)).toBe(html);
  });
});
