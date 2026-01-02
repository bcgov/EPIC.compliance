// cypress/components/ControlledAutoComplete.cy.tsx
import { mount } from "cypress/react";
import { useForm, FormProvider } from "react-hook-form";
import ControlledAutoComplete from "@/components/Shared/Controlled/ControlledAutoComplete";

interface Option {
  label: string;
  value: string;
}

interface ITestComp {
  options?: Option[],
  multiple?: boolean,
  onDeleteOption?: (option) => void,
  onChange?: (option) => void,
}

const optionsList: Option[] = [
  { label: "Option 1", value: "option1" },
  { label: "Option 2", value: "option2" },
  { label: "Option 3", value: "option3" },
];

const TestComponent = ({ options = optionsList, multiple = false, onDeleteOption, onChange }: ITestComp) => {
  const methods = useForm({
    defaultValues: {
      testAutocomplete: multiple ? [] : null,
    },
  });

  return (
    <FormProvider {...methods}>
      <form>
        <ControlledAutoComplete<Option>
          name="testAutocomplete"
          label="Test Autocomplete"
          options={options}
          getOptionLabel={(option) => option.label}
          isOptionEqualToValue={(option, value) => option.value === value.value}
          multiple={multiple}
          onDeleteOption={onDeleteOption}
          onChange={onChange}
        />
      </form>
    </FormProvider>
  );
};

describe("ControlledAutoComplete", () => {
  it("renders correctly", () => {
    mount(<TestComponent />);
    cy.get("input[name='testAutocomplete']").should("exist");
  });

  it("displays options when focused", () => {
    mount(<TestComponent />);
    cy.get("input[name='testAutocomplete']").click();
    cy.get("li[data-option-index]").should("have.length", optionsList.length);
  });

  it("allows selecting an option", () => {
    mount(<TestComponent />);
    cy.get("input[name='testAutocomplete']").click();
    cy.get("li[data-option-index='0']").click();
    cy.get("input[name='testAutocomplete']").should(
      "have.value",
      optionsList[0].label
    );
  });

  it("displays an error message when validation fails", () => {
    const errorMessage = "This field is required";
    const TestComponentWithValidation = () => {
      const methods = useForm({
        defaultValues: {
          testAutocomplete: null,
        },
        mode: "onSubmit",
        resolver: async (data) => {
          return {
            values: data,
            errors: data.testAutocomplete
              ? {}
              : { testAutocomplete: { message: errorMessage } },
          };
        },
      });

      return (
        <FormProvider {...methods}>
          <form onSubmit={methods.handleSubmit(() => {})}>
            <ControlledAutoComplete<Option>
              name="testAutocomplete"
              label="Test Autocomplete"
              options={optionsList}
              getOptionLabel={(option) => option.label}
              isOptionEqualToValue={(option, value) =>
                option.value === value.value
              }
            />
            <button type="submit">Submit</button>
          </form>
        </FormProvider>
      );
    };

    mount(<TestComponentWithValidation />);
    cy.get("button[type='submit']").click();
    cy.get("p.Mui-error").should("contain.text", errorMessage);
  });

  it("supports multiple selection", () => {
    mount(<TestComponent multiple={true} />);
    cy.get("input[name='testAutocomplete']").click();
    cy.get("li[data-option-index='0']").click();
    cy.get("li[data-option-index='1']").click();
    cy.get("div.MuiChip-root").should("have.length", 2);
    cy.get("div.MuiChip-root").first().should("contain.text", optionsList[0].label);
  });

  it("calls onDeleteOption when deleting a chip", () => {
    const onDeleteOption = cy.stub();
    mount(<TestComponent multiple={true} onDeleteOption={onDeleteOption} />);
    cy.get("input[name='testAutocomplete']").click();
    cy.get("li[data-option-index='0']").click();
    cy.get("li[data-option-index='1']").click();
    cy.get("div.MuiChip-root").first().find("svg").click(); // Click the delete icon on the chip
    cy.wrap(onDeleteOption).should("have.been.calledOnceWith", optionsList[0]);
  });

  it("updates the selected value when multiple is enabled and chip is deleted", () => {
    mount(<TestComponent multiple={true} />);
    cy.get("input[name='testAutocomplete']").click();
    cy.get("li[data-option-index='0']").click();
    cy.get("li[data-option-index='1']").click();
    cy.get("div.MuiChip-root").should("have.length", 2);
    cy.get("div.MuiChip-root").first().find("svg").click(); // Click the delete icon
    cy.get("div.MuiChip-root").should("have.length", 1);
    cy.get("div.MuiChip-root").first().should("contain.text", optionsList[1].label);
  });

  it("renders the placeholder correctly", () => {
    mount(<TestComponent />);
    cy.get("input[name='testAutocomplete']").should(
      "have.attr",
      "placeholder",
      "Select an option..."
    );
  });

  it("calls the custom onChange handler when an option is selected", () => {
    const handleChange = cy.stub().as("onChangeHandler");

    mount(<TestComponent onChange={handleChange} />);
    cy.get("input[name='testAutocomplete']").click();
    cy.get("li[data-option-index='0']").click();

    // Check if the onChange handler was called with the correct arguments
    cy.get("@onChangeHandler").should(
      "have.been.calledWith",
      Cypress.sinon.match.any, // The synthetic event (_event) parameter
      optionsList[0], // The new value (newVal)
      "selectOption" // The action type
    );
  });

  it("sets the correct value based on the 'multiple' prop", () => {
    // Test with multiple = true
    mount(<TestComponent multiple={true} />);
    cy.get("input[name='testAutocomplete']").click();
    cy.get("li[data-option-index='0']").click();
    cy.get("div.MuiChip-root").should("have.length", 1);

    // Test with multiple = false
    mount(<TestComponent multiple={false} />);
    cy.get("input[name='testAutocomplete']").click();
    cy.get("li[data-option-index='1']").click();
    cy.get("input[name='testAutocomplete']").should(
      "have.value",
      optionsList[1].label
    );
  });
});
