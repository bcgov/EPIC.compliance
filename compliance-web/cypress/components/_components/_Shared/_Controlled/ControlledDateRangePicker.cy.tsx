import { mount } from "cypress/react";
import { FormProvider, useForm } from "react-hook-form";
import ControlledDateRangePicker from "@/components/Shared/Controlled/ControlledDateRangePicker";
import { LocalizationProvider } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

describe("ControlledDateRangePicker Component", () => {
  const currentDay = new Date();
  const currentYear = currentDay.getFullYear();
  const currentMonth = String(currentDay.getMonth() + 1).padStart(2, "0");

  const TestComponent = () => {
    const methods = useForm({
      defaultValues: {
        dateRangeField: { startDate: null, endDate: null },
      },
      mode: "onChange",
    });

    return (
      <FormProvider {...methods}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <ControlledDateRangePicker name="dateRangeField" label="Date Field" />
          <button type="submit">Submit</button>
        </LocalizationProvider>
      </FormProvider>
    );
  };

  it("renders the date picker component", () => {
    mount(<TestComponent />);
    cy.get("input").should("exist");
    cy.get("input").should(
      "have.attr",
      "placeholder",
      "YYYY-MM-DD — YYYY-MM-DD"
    );
  });

  it("should open date calender on date range click", () => {
    mount(<TestComponent />);
    cy.get("input").click();
    cy.get(".MuiDateCalendar-root").should("be.visible");
  });

  it("should change date range", () => {
    mount(<TestComponent />);
    const startDay = "14";
    const endDay = "17";
    cy.get("input").click();
    cy.get(".MuiDateCalendar-root").should("be.visible");
    cy.get(".MuiPickersDay-root").contains(startDay).click();
    cy.get(".MuiPickersDay-root").contains(endDay).click();
    cy.get("input").should(
      "have.value",
      `${currentYear}-${currentMonth}-${startDay} — ${currentYear}-${currentMonth}-${endDay}`
    );
  });

  it("should change date range and click away", () => {
    mount(<TestComponent />);
    const startDay = "13";
    cy.get("input").click();
    cy.get(".MuiDateCalendar-root").should("be.visible");
    cy.get(".MuiPickersDay-root").contains(startDay).click();
    cy.get(".MuiPopover-root").click(0,0);
    cy.get("input").should(
      "have.value",
      `${currentYear}-${currentMonth}-${startDay} -`
    );
  });

  it("displays validation error", () => {
    const TestComponentWithValidation = () => {
      const methods = useForm({
        defaultValues: {
          dateRangeField: { startDate: null, endDate: null },
        },
        mode: "onChange",
        resolver: async (data) => {
          return {
            values: data,
            errors: !data.dateRangeField.startDate
              ? {
                  dateRangeField: {
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
              <ControlledDateRangePicker
                name="dateRangeField"
                label="Date Field"
              />
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
