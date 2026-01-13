// import { mount } from "cypress/react";
// import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// import { Inspections } from "@/routes/_authenticated/ce-database/inspections";
// import router from "@/router/router";
// import DrawerProvider from "@/components/Shared/Drawer/DrawerProvider";
// import { LocalizationProvider } from "@mui/x-date-pickers";
// import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

// describe("Inspections Component", () => {
//   const queryClient = new QueryClient();

//   function mountInspections(): React.ReactNode {
//     return (
//       <QueryClientProvider client={queryClient}>
//         <LocalizationProvider dateAdapter={AdapterDayjs}>
//           <DrawerProvider />
//           <Inspections />
//         </LocalizationProvider>
//       </QueryClientProvider>
//     );
//   }

//   it("should render inspections page correctly", () => {
//     router.navigate({ to: "/ce-database/inspections" });

//     // mount(mountInspections());

//     // cy.contains("h5", "Inspections").should("be.visible");
//     // cy.get("button").should("contain.text", "Inspection");
//   });

//   // it("should render inspections table correctly", () => {
//   //   router.navigate({ to: "/ce-database/inspections" });

//   //   mount(mountInspections());

//   //   cy.get("table").should("be.visible");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "IR #");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Project");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Stage");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Type");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Status");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Primary");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Case File #");
//   // });

//   // it("should open the Inspections modal when the add button is clicked", () => {
//   //   router.navigate({ to: "/ce-database/inspections" });

//   //   mount(mountInspections());

//   //   cy.get("button").contains("Inspection").click();

//   //   cy.get(".MuiTypography-subtitle1").should("contain.text", "Create Inspection")

//   // });
// });
