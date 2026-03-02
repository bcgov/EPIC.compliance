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

export function setAuthToken(client: AxiosInstance) {
  const user = getUser();
  if (user?.access_token) {
    client.defaults.headers.common.Authorization = `Bearer ${user?.access_token}`;
  } else {
    throw new Error("No access token!");
  }
}

export const request = ({ ...options }) => {
  const client = axios.create({ baseURL: AppConfig.apiUrl });
  setAuthToken(client);
  return client(options).then(onSuccess).catch(onError);
};

export const requestAuthAPI = ({ ...options }) => {
  const client = axios.create({ baseURL: AppConfig.authAPIUrl });
  setAuthToken(client);
  return client(options).then(onSuccess).catch(onError);
};

export const requestTrackAPI = ({ ...options }) => {
  const client = axios.create({ baseURL: AppConfig.trackAPIUrl });
  setAuthToken(client);
  return client(options).then(onSuccess).catch((error: AxiosError<ErrorResponseData>) => {
    if (error.code === 'ERR_NETWORK') {
      notify.error('Track API is currently unavailable. Please try again later.');
      throw error;
    }
    return onError(error);
  });
};

export const requestDocumentAPI = ({ ...options }) => {
  const client = axios.create({ baseURL: AppConfig.documentAPIUrl });
  setAuthToken(client);
  return client(options).then(onSuccess).catch(onError);
};

export const requestAxios = ({ ...options }) => {
  const client = axios.create(options);
  return client(options).then(onSuccess).catch(onError);
};
