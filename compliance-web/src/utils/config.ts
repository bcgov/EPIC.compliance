declare global {
  interface Window {
    _env_: {
      VITE_API_URL: string;
      VITE_AUTH_API_URL: string;
      VITE_TRACK_API_URL: string;
      VITE_DOCUMENT_API_URL: string;
      VITE_ENV: string;
      VITE_VERSION: string;
      VITE_APP_TITLE: string;
      VITE_APP_BASE_PATH: string;
      VITE_APP_URL: string;
      VITE_OIDC_AUTHORITY: string;
      VITE_CLIENT_ID: string;
      VITE_DEFAULT_PAGE_SIZE: number;
      VITE_INPROGRESS_FEATURES: string[];
      VITE_CENTRE_API_URL: string;
    };
  }
}
const API_URL =
  window._env_?.VITE_API_URL || import.meta.env.VITE_API_URL || "";
const AUTH_API_URL =
  window._env_?.VITE_AUTH_API_URL || import.meta.env.VITE_AUTH_API_URL || "";
const TRACK_API_URL =
  window._env_?.VITE_TRACK_API_URL || import.meta.env.VITE_TRACK_API_URL || "";
const DOCUMENT_API_URL =
  window._env_?.VITE_DOCUMENT_API_URL || import.meta.env.VITE_DOCUMENT_API_URL || "";
const APP_ENVIRONMENT =
  window._env_?.VITE_ENV || import.meta.env.VITE_ENV || "";
const APP_VERSION =
  window._env_?.VITE_VERSION || import.meta.env.VITE_VERSION || "";
const APP_TITLE =
  window._env_?.VITE_APP_TITLE || import.meta.env.VITE_APP_TITLE || "";
const APP_BASE_PATH = window._env_?.VITE_APP_BASE_PATH || import.meta.env.VITE_APP_BASE_PATH;
const APP_URL = window._env_?.VITE_APP_URL || import.meta.env.VITE_APP_URL;
const OIDC_AUTHORITY = window._env_?.VITE_OIDC_AUTHORITY || import.meta.env.VITE_OIDC_AUTHORITY;
const CLIENT_ID = window._env_?.VITE_CLIENT_ID || import.meta.env.VITE_CLIENT_ID;
const DEFAULT_PAGE_SIZE = window._env_?.VITE_DEFAULT_PAGE_SIZE || import.meta.env.VITE_DEFAULT_PAGE_SIZE || 15;
const INPROGRESS_FEATURES = window._env_?.VITE_INPROGRESS_FEATURES || import.meta.env.VITE_INPROGRESS_FEATURES;
const CENTRE_API_URL = window._env_?.VITE_CENTRE_API_URL || import.meta.env.VITE_CENTRE_API_URL || "";

export const AppConfig = {
  apiUrl: `${API_URL}/api`,
  authAPIUrl: `${AUTH_API_URL}/api`,
  trackAPIUrl: `${TRACK_API_URL}/api/v1`,
  documentAPIUrl: `${DOCUMENT_API_URL}/api`,
  centreAPIUrl: CENTRE_API_URL,
  environment: APP_ENVIRONMENT,
  version: APP_VERSION,
  appTitle: APP_TITLE,
  appBasePath: APP_BASE_PATH,
  inprogressFeatures: INPROGRESS_FEATURES,
  defaultPageSize: DEFAULT_PAGE_SIZE,
};

export const OidcConfig = {
  authority: OIDC_AUTHORITY,
  client_id: CLIENT_ID,
  redirect_uri: `${APP_URL}${APP_BASE_PATH || ''}/oidc-callback`,
  post_logout_redirect_uri: `${APP_URL}${APP_BASE_PATH || ''}/`,
  scope: "openid profile email",
  response_type: "code",
  automaticSilentRenew: false,
  revokeTokensOnSignout: true,
  extraQueryParams: {
    kc_idp_hint: "idir"
  },
};
