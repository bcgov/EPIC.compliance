// @vitest-environment jsdom
import { describe, expect, it } from "vitest";
import { sanitizeHtml, sanitizeReportHtml } from "./sanitizeHtml";

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

describe("sanitizeReportHtml", () => {
  const doc = (body: string) =>
    `<!DOCTYPE html><html><head><title>t</title><style>table{border:1px solid black}</style></head><body>${body}</body></html>`;

  it("preserves the document's style block and table layout", () => {
    const result = sanitizeReportHtml(
      doc('<table><colgroup><col style="width:92px"></colgroup><tr><th>A</th></tr></table>')
    );
    expect(result).toContain("<style>table{border:1px solid black}</style>");
    expect(result).toContain("<colgroup>");
    expect(result).toContain('<col style="width:92px">');
  });

  it("strips script tags", () => {
    const result = sanitizeReportHtml(doc("<script>alert(1)</script>"));
    expect(result).not.toContain("<script");
    expect(result).not.toContain("alert(1)");
  });

  it("strips onerror event handler payloads from img tags", () => {
    const result = sanitizeReportHtml(doc('<img src="x" onerror="alert(1)">'));
    expect(result).not.toContain("onerror");
  });

  it("strips javascript: URIs from links", () => {
    const result = sanitizeReportHtml(doc('<a href="javascript:alert(1)">click</a>'));
    expect(result).not.toContain("javascript:");
  });

  it("strips iframe, object, and form elements", () => {
    const result = sanitizeReportHtml(
      doc('<iframe src="https://evil.com"></iframe><object data="https://evil.com"></object><form action="https://evil.com"><input></form>')
    );
    expect(result).not.toContain("<iframe");
    expect(result).not.toContain("<object");
    expect(result).not.toContain("<form");
  });
});
