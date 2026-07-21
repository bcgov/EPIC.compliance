import DOMPurify from "dompurify";

const ALLOWED_TAGS = [
  "p", "br", "div", "span", "hr",
  "b", "strong", "i", "em", "u", "s", "strike",
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
