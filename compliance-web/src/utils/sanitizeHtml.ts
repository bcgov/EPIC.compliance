import DOMPurify from "dompurify";

const ALLOWED_TAGS = [
  "p", "br", "div", "span", "hr",
  "b", "strong", "i", "em", "u", "s", "strike", "mark",
  "ul", "ol", "li",
  "h1", "h2", "h3", "h4", "h5", "h6",
  "blockquote",
  "table", "thead", "tbody", "tr", "td", "th",
  "a", "img",
];

const ALLOWED_ATTR = [
  "style", "class", "href", "target", "rel",
  "src", "alt", "width", "height", "colspan", "rowspan",
];

/**
 * Sanitizes editor/report-authored HTML before it is rendered via
 * dangerouslySetInnerHTML or assigned to innerHTML, stripping scripts,
 * event handlers, and anything outside the formatting allow-list.
 */
export const sanitizeHtml = (html: string): string => {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
    ALLOW_DATA_ATTR: true,
  });
};

/**
 * Sanitizes a full HTML *document* (doctype/html/head/body, <style>,
 * <colgroup>/<col>) as returned by epic.document for the report preview.
 * Unlike sanitizeHtml(), this keeps the document's own layout/print CSS
 * intact instead of applying the formatting-tag allow-list meant for
 * small editor-authored fragments. DOMPurify still unconditionally strips
 * <script>, event handler attributes, and javascript: URIs; the extra
 * FORBID_TAGS remove other executable/navigable elements the default
 * profile would otherwise keep (iframe, object, embed, form, etc.).
 */
export const sanitizeReportHtml = (html: string): string => {
  return DOMPurify.sanitize(html, {
    WHOLE_DOCUMENT: true,
    FORBID_TAGS: ["iframe", "object", "embed", "form", "base", "link", "meta"],
  });
};
