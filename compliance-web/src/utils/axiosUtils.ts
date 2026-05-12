/* eslint-disable @typescript-eslint/no-explicit-any */
import { notify } from "@/store/snackbarStore";
import { AppConfig, OidcConfig } from "@/utils/config";
import axios, { AxiosError, AxiosInstance } from "axios";
import { User } from "oidc-client-ts";

export type OnErrorType = (error: AxiosError) => void;
export type OnSuccessType = (data: any) => void;

type ErrorResponseData = {
  message?: string;
  error?: string;
  details?: string;
};

export function getUser() {
  const oidcStorage = sessionStorage.getItem(
    `oidc.user:${OidcConfig.authority}:${OidcConfig.client_id}`
  );
  if (!oidcStorage) {
    return null;
  }

  return User.fromStorageString(oidcStorage);
}

const onSuccess = (response: any) => response?.data ?? response.data;

export const onError = (error: AxiosError<ErrorResponseData>) => {  
  // No response - network/connection error
  if (!error.response) {
    const errorMessage = error.code === 'ERR_NETWORK' 
      ? 'Network error. Please refresh the page to try again.'
      : error.code === 'ECONNABORTED'
      ? 'Request timeout. Please try again.'
      : 'Unable to reach the server. Please try again later.';
    
    notify.error(errorMessage);
    throw error;
  }

  // Extract error message from response
  const { status, data } = error.response;
  
  // Try to get the specific error message
  const errorMessage = 
    data?.message || 
    data?.error || 
    data?.details ||
    `Request failed with status ${status}`;

  notify.error(errorMessage, 3000);
  throw error;
};

function addAuthInterceptor(client: AxiosInstance) {
  client.interceptors.request.use((config) => {
    const user = getUser();
    if (user?.access_token) {
      config.headers.Authorization = `Bearer ${user.access_token}`;
    } else {
      throw new Error("No access token!");
    }
    return config;
  });
}

const apiClient = axios.create({ baseURL: AppConfig.apiUrl });
addAuthInterceptor(apiClient);

const authAPIClient = axios.create({ baseURL: AppConfig.authAPIUrl });
addAuthInterceptor(authAPIClient);

const trackAPIClient = axios.create({ baseURL: AppConfig.trackAPIUrl });
addAuthInterceptor(trackAPIClient);

const documentAPIClient = axios.create({ baseURL: AppConfig.documentAPIUrl });
addAuthInterceptor(documentAPIClient);

export const request = ({ ...options }) => {
  return apiClient(options).then(onSuccess).catch(onError);
};

export const requestAuthAPI = ({ ...options }) => {
  return authAPIClient(options).then(onSuccess).catch(onError);
};

export const requestTrackAPI = ({ ...options }) => {
  return trackAPIClient(options).then(onSuccess).catch(onError);
};

export const requestDocumentAPI = ({ ...options }) => {
  return documentAPIClient(options).then(onSuccess).catch(onError);
};

export const requestAxios = ({ ...options }) => {
  const client = axios.create(options);
  return client(options).then(onSuccess).catch(onError);
};
