import RequirementFormLeftEditSection from "@/components/App/Inspections/Profile/Requirements/RequirementFormLeftEditSection";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { FormProvider, useForm } from "react-hook-form";
import { EnforcementActionEnum } from "@/utils/constants";
import { mockInspection } from "./mockData";

// Same order as the API's sort_order
const mockEnforcementActions = [
  { id: EnforcementActionEnum.TO_BE_DETERMINED, name: "To Be Determined" },
  { id: EnforcementActionEnum.NOT_APPLICABLE, name: "Not Applicable" },
  { id: "3", name: "Notice of Non-Compliance" },
  { id: EnforcementActionEnum.WARNING_LETTER, name: "Warning Letter" },
  { id: EnforcementActionEnum.ORDER, name: "Order" },
  { id: EnforcementActionEnum.ADVISORY, name: "Advisory" },
  { id: EnforcementActionEnum.WARNING, name: "Warning" },
  { id: EnforcementActionEnum.RESTORATIVE_JUSTICE, name: "Restorative Justice" },
];

describe("RequirementFormLeftEditSection Component", () => {
  const mountComponent = (isHistory: boolean) => {
    const queryClient = new QueryClient();
    queryClient.setQueryData(["enforcement-actions"], mockEnforcementActions);

    const Wrapper = ({ children }: { children: React.ReactNode }) => {
      const methods = useForm({ defaultValues: { enforcementAction: null } });
      return (
        <QueryClientProvider client={queryClient}>
          <FormProvider {...methods}>{children}</FormProvider>
        </QueryClientProvider>
      );
    };

    cy.mount(
      <Wrapper>
        <RequirementFormLeftEditSection
          inspectionData={{ ...mockInspection, is_history: isHistory }}
        />
      </Wrapper>
    );
  };

  const openEnforcementActionDropdown = () => {
    cy.contains("label", "Enforcement Action").parent().find("input").click();
  };

  it("lists Advisory between Not Applicable and Notice of Non-Compliance for regular inspections", () => {
    mountComponent(false);
    openEnforcementActionDropdown();

    cy.get('[role="option"]').then((options) => {
      const names = [...options].map((option) => option.innerText.trim());
      expect(names).to.deep.equal([
        "To Be Determined",
        "Not Applicable",
        "Advisory",
        "Notice of Non-Compliance",
        "Warning Letter",
        "Order",
      ]);
    });
  });

  it("does not show the Historical badge for regular inspections", () => {
    mountComponent(false);
    openEnforcementActionDropdown();

    cy.contains('[role="option"]', "Advisory").should("be.visible");
    cy.contains("Historical").should("not.exist");
  });

  it("keeps Advisory and Warning at the end with the Historical badge for historical inspections", () => {
    mountComponent(true);
    openEnforcementActionDropdown();

    cy.get('[role="option"]').then((options) => {
      const names = [...options].map((option) =>
        option.innerText.replace("Historical", "").trim()
      );
      expect(names).to.deep.equal([
        "To Be Determined",
        "Not Applicable",
        "Notice of Non-Compliance",
        "Warning Letter",
        "Order",
        "Advisory",
        "Warning",
      ]);
    });
    cy.get('[role="option"]').eq(4).should("not.contain", "Historical");
    cy.get('[role="option"]').eq(5).should("contain", "Historical");
    cy.get('[role="option"]').eq(6).should("contain", "Historical");
  });
});
