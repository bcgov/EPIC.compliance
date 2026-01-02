// import { mount } from "cypress/react";
// import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// import { CaseFiles } from "@/routes/_authenticated/ce-database/case-files";
// import router from "@/router/router";
// import DrawerProvider from "@/components/Shared/Drawer/DrawerProvider";
// import { LocalizationProvider } from "@mui/x-date-pickers";
// import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

// describe("CaseFiles Component", () => {
//   const queryClient = new QueryClient();

//   function mountCaseFiles(): React.ReactNode {
//     return (
//       <QueryClientProvider client={queryClient}>
//         <LocalizationProvider dateAdapter={AdapterDayjs}>
//           <DrawerProvider />
//           <CaseFiles />
//         </LocalizationProvider>
//       </QueryClientProvider>
//     );
//   }

//   it("should render case files page correctly", () => {
//     router.navigate({ to: "/ce-database/case-files" });

//     // mount(mountCaseFiles());

//     // cy.contains("h5", "Case Files").should("be.visible");
//     // cy.get("button").should("contain.text", "Case File");
//   });

//   // it("should render case files table correctly", () => {
//   //   router.navigate({ to: "/ce-database/case-files" });

//   //   mount(mountCaseFiles());

//   //   cy.get("table").should("be.visible");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Case File #");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Project");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Initiation");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Date Created");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Status");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Primary");
//   // });

//   // it("should open the Case Files modal when the add button is clicked", () => {
//   //   router.navigate({ to: "/ce-database/case-files" });

//   //   mount(mountCaseFiles());

//   //   cy.get("button").contains("Case File").click();

//   //   cy.get(".MuiTypography-subtitle1").should("contain.text", "Create Case File")

//   // });
// });
