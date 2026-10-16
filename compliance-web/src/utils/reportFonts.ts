const LOCAL_CALIBRI_FACES: Record<string, string> = {
  regular: "local('Calibri'), local('Calibri-Regular')",
  italic: "local('Calibri Italic'), local('Calibri-Italic')",
  bold: "local('Calibri Bold'), local('Calibri-Bold')",
  "bold-italic": "local('Calibri Bold Italic'), local('Calibri-BoldItalic')",
};

const REMOTE_CALIBRI_SRC =
  /url\(\s*(['"]?)[^'")]*\/calibri-(regular|italic|bold|bold-italic)\.ttf\1\s*\)(\s*format\(\s*(['"])truetype\4\s*\))?/g;

/**
 * Points the report templates' Calibri @font-face rules at the locally
 * installed font instead of the object store. Browsers fetch @font-face
 * sources in CORS mode and the static-assets bucket rejects any request
 * carrying an Origin header (403 InvalidCorsRequest), so the in-page preview
 * cannot load them. The DOCX download names Calibri directly and never used
 * the remote fonts; machines without Calibri fall back to the template's
 * 'BC Sans', sans-serif stack.
 */
export const localizeReportFonts = (html: string): string =>
  html.replace(REMOTE_CALIBRI_SRC, (_match, _quote, variant: string) => LOCAL_CALIBRI_FACES[variant]);
