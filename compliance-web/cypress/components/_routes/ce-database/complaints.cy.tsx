// import { mount } from "cypress/react";
// import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// import { Complaints } from "@/routes/_authenticated/ce-database/complaints";
// import router from "@/router/router";
// import DrawerProvider from "@/components/Shared/Drawer/DrawerProvider";
// import { LocalizationProvider } from "@mui/x-date-pickers";
// import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

// describe("Complaints Component", () => {
//   const queryClient = new QueryClient();

//   function mountComplaints(): React.ReactNode {
//     return (
//       <QueryClientProvider client={queryClient}>
//         <LocalizationProvider dateAdapter={AdapterDayjs}>
//           <DrawerProvider />
//           <Complaints />
//         </LocalizationProvider>
//       </QueryClientProvider>
//     );
//   }

//   it("should render complaints page correctly", () => {
//     router.navigate({ to: "/ce-database/complaints" });

//     // mount(mountComplaints());

//     // cy.contains("h5", "Complaints").should("be.visible");
//     // cy.get("button").should("contain.text", "Complaint");
//   });

//   // it("should render complaints table correctly", () => {
//   //   router.navigate({ to: "/ce-database/complaints" });

//   //   mount(mountComplaints());

//   //   cy.get("table").should("be.visible");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "IR #");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Project");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Stage");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Type");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Status");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Primary");
//   //   cy.get(".Mui-TableHeadCell-Content").should("contain.text", "Case File #");
//   // });

//   // it("should open the Complaints modal when the add button is clicked", () => {
//   //   router.navigate({ to: "/ce-database/complaints" });

//   //   mount(mountComplaints());

//   //   cy.get("button").contains("Complaint").click();

//   //   cy.get(".MuiTypography-subtitle1").should("contain.text", "Create Complaint")

//   // });
// });
