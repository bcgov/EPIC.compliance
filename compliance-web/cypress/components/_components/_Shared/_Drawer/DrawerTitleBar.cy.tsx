/// <reference types="cypress" />
import { mount } from "cypress/react";
import DrawerTitleBar from "@/components/Shared/Drawer/DrawerTitleBar"; // Adjust path accordingly
import { FormProvider, useForm } from "react-hook-form";
import { useDrawer } from "@/store/drawerStore";
import { useModal } from "@/store/modalStore";
import { TextField } from "@mui/material";

describe("DrawerTitleBar Component", () => {
  beforeEach(() => {
    // Reset the Zustand stores before each test
    useDrawer.setState({
      isOpen: true,
      drawerContent: null,
      setOpen: cy.stub().as("setOpen"),
      setClose: cy.stub().as("setClose"),
    });

    useModal.setState({
      setOpen: cy.stub().as("setModalOpen"),
      setClose: cy.stub().as("setModalClose"),
    });

    // Mount the component within a form context using react-hook-form
    const Wrapper = ({ children }: { children: React.ReactNode }) => {
      const methods = useForm({
        defaultValues: {
          testField: "default value",
        },
      });

      return (
        <FormProvider {...methods}>
          <form>
            {children}
            <TextField name="testField" label="Test Field" />
          </form>
        </FormProvider>
      );
    };

    mount(
      <Wrapper>
        <DrawerTitleBar title="Test Drawer" isFormDirtyCheck={true} />
      </Wrapper>
    );
  });

  it("renders with the provided title", () => {
    cy.contains("Test Drawer").should("exist");
  });

  it("closes the drawer when close icon is clicked and there are no unsaved changes", () => {
    // Simulate no unsaved changes
    cy.get('button[aria-label="close"]').click();
    cy.get("@setClose").should("have.been.calledOnce");
  });
});
