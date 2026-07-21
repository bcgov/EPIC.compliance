// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { sanitizeHtml } from "./sanitizeHtml";

describe("sanitizeHtml", () => {
  it("strips script tags", () => {
    const result = sanitizeHtml('<p>hello</p><script>alert(1)</script>');
    expect(result).toBe("<p>hello</p>");
  });

  it("strips onerror event handler payloads from img tags", () => {
    const result = sanitizeHtml('<img src="x" onerror="alert(1)">');
    expect(result).not.toContain("onerror");
    expect(result).not.toContain("alert(1)");
  });

  it("strips javascript: URIs from links", () => {
    const result = sanitizeHtml('<a href="javascript:alert(1)">click</a>');
    expect(result).not.toContain("javascript:");
  });

  it("preserves allow-listed formatting tags and attributes", () => {
    const html = '<p style="color: red;"><strong>Bold</strong> and <em>italic</em></p>';
    expect(sanitizeHtml(html)).toBe(html);
  });
});
