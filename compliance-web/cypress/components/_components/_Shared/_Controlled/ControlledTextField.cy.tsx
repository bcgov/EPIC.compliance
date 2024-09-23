/// <reference types="cypress" />
import ControlledTextField from "@/components/Shared/Controlled/ControlledTextField"; // Update with the correct path
import { FormProvider, useForm } from "react-hook-form";
import { mount } from "cypress/react18";

describe("ControlledTextField Component", () => {
  const setup = (props = {}) => {
    const Wrapper = () => {
      const methods = useForm({
        defaultValues: {
          testField: "defaultValue",
        },
      });

      return (
        <FormProvider {...methods}>
          <ControlledTextField name="testField" {...props} />
        </FormProvider>
      );
    };

    mount(<Wrapper />);
  };

  it("renders without crashing", () => {
    setup();
    cy.get('input[name="testField"]').should("exist");
  });

  it("displays the default value", () => {
    setup();
    cy.get('input[name="testField"]').should("have.value", "defaultValue");
  });

  it("displays an error message when there is an error", () => {
    const errorMessage = "This field is required";
    setup({
      name: "testField",
      rules: { required: errorMessage },
      helperText: errorMessage,
      error: true,
    });
    cy.get('input[name="testField"]').focus().blur();
    cy.get(".MuiFormHelperText-root").should("contain.text", errorMessage);
  });

  it("limits input value length based on maxLength prop", () => {
    setup({ maxLength: 5 });
    cy.get('input[name="testField"]')
      .clear()
      .type("123456")
      .should("have.value", "12345");
  });

  it("triggers onChange function passed as a prop", () => {
    const handleChange = cy.stub();
    setup({ onChange: handleChange });

    cy.get('input[name="testField"]').type("test");
    cy.wrap(handleChange).should("be.called");
  });

  it("applies inputEffects function to the input value", () => {
    const inputEffects = (e) => e.target.value.toUpperCase();
    setup({ inputEffects });

    cy.get('input[name="testField"]').clear().type("test").should("have.value", "TEST");
  });
});
