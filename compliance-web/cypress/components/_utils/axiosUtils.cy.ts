/// <reference types="cypress" />

import { getUser } from "@/utils/axiosUtils";
import axios, { AxiosResponse } from "axios";
import { User } from "oidc-client-ts";
import { AxiosError } from "axios";
import { onError } from "@/utils/axiosUtils";
import { notify } from "@/store/snackbarStore";

describe("axiosUtils", () => {
  beforeEach(() => {
    // Reset session storage and axios defaults before each test
    sessionStorage.clear();
    axios.defaults.headers.common.Authorization = undefined;
  });

  describe("getUser", () => {
    it("should return null if no oidcStorage is found", () => {
      cy.stub(sessionStorage, "getItem").returns(null);
      expect(getUser()).to.be.null;
    });

    it("should return a User object if oidcStorage is found", () => {
      const oidcStorageMock = '{"access_token":"mockAccessToken"}';
      cy.stub(sessionStorage, "getItem").returns(oidcStorageMock);
      cy.stub(User, "fromStorageString").returns({
        access_token: "mockAccessToken",
      } as User);
      const user = getUser();
      expect(user).to.have.property("access_token", "mockAccessToken");
    });
  });

  describe("error handling", () => {
   it("should handle network errors (ERR_NETWORK)", () => {
      const error = new AxiosError();
      error.response = undefined;
      error.code = "ERR_NETWORK";

      cy.stub(notify, "error");

      // Assert it throws error
      expect(() => onError(error)).to.throw();

      expect(notify.error).to.be.calledWith(
        "Network error. Please refresh the page to try again."
      );
    });

    it("should handle request timeouts (ECONNABORTED)", () => {
      const error = new AxiosError();
      error.response = undefined;
      error.code = "ECONNABORTED";

      cy.stub(notify, "error");

      expect(() => onError(error)).to.throw();
      expect(notify.error).to.be.calledWith("Request timeout. Please try again.");
    });

    it("should handle other network issues", () => {
      const error = new AxiosError();
      error.response = undefined;
      error.code = "SOME_OTHER_ERROR";

      cy.stub(notify, "error");

      expect(() => onError(error)).to.throw();
      expect(notify.error).to.be.calledWith(
        "Unable to reach the server. Please try again later."
      );
    });

    it("should handle API errors with custom message", () => {
      const error = new AxiosError();
      error.response = { data: { message: "Custom API Error" } } as AxiosResponse;
      
      cy.stub(notify, "error");
      expect(() => onError(error)).to.throw();
      expect(notify.error).to.be.calledWith("Custom API Error");
    });
  });

});
