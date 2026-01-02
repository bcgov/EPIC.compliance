
import { mount } from "cypress/react";
import { FormProvider, useForm } from "react-hook-form";
import ControlledDateField from "@/components/Shared/Controlled/ControlledDateField";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

describe("ControlledDateField Component", () => {
  const TestComponent = () => {
    const methods = useForm({
      defaultValues: {
        dateField: null,
      },
      mode: "onChange",
    });

    return (
      <FormProvider {...methods}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <ControlledDateField name="dateField" label="Date Field" />
          <button type="submit">Submit</button>
        </LocalizationProvider>
      </FormProvider>
    );
  };

  it("renders the date picker component", () => {
    mount(<TestComponent />);
    cy.get("input").should("exist");
    cy.get("input").should("have.attr", "placeholder", "YYYY-MM-DD");
  });

  it("should handle date change", () => {
    mount(<TestComponent />);
    const testDate = "2024-08-15";
    cy.get("input").type(testDate);
    cy.get("input").should("have.value", "2024-08-15");
  });

  it("displays validation error", () => {
    const TestComponentWithValidation = () => {
      const methods = useForm({
        defaultValues: {
          dateField: null,
        },
        mode: "onChange",
        resolver: async (data) => {
          return {
            values: data,
            errors: !data.dateField
              ? {
                  dateField: {
                    type: "required",
                    message: "Date is required",
                  },
                }
              : {},
          };
        },
      });

      return (
        <FormProvider {...methods}>
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <form onSubmit={methods.handleSubmit(() => {})}>
              <ControlledDateField name="dateField" label="Date Field" />
              <button type="submit">Submit</button>
            </form>
          </LocalizationProvider>
        </FormProvider>
      );
    };

    mount(<TestComponentWithValidation />);
    cy.get("button[type='submit']").click();
    cy.get("p.Mui-error").should("contain", "Date is required");
  });
});
