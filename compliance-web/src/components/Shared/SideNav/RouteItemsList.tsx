import {
  FormatListBulletedRounded,
  SettingsRounded,
  ViewKanbanRounded,
} from "@mui/icons-material";

export interface RouteMenuItem {
  routeName: string;
  path?: string;
  icon?: JSX.Element;
  subRoutes?: RouteMenuItem[];
}

export default function RouteItemsList() {
  const routeMenuItems: RouteMenuItem[] = [
    {
      routeName: "C&E Database",
      icon: <FormatListBulletedRounded />, 
      subRoutes: [
        {
          routeName: "Case Files",
          path: "/ce-database/case-files",
        },
        {
          routeName: "Inspections",
          path: "/ce-database/inspections",
        },
        {
          routeName: "Complaints",
          path: "/ce-database/complaints",
        },
        {
          routeName: "Requirements",
          path: "/ce-database/requirements",
        },
        {
          routeName: "Reports",
          path: "/ce-database/reports",
        },
      ],
    },
    {
      routeName: "Review Board",
      icon: <ViewKanbanRounded />,
      path: "/review-board",
    },
    {
      routeName: "Admin",
      icon: <SettingsRounded />,
      subRoutes: [
        {
          routeName: "Staff",
          path: "/admin/staff",
        },
        {
          routeName: "Agencies",
          path: "/admin/agencies",
        },
        {
          routeName: "Topics",
          path: "/admin/topics",
        },
      ],
    },
  ];

  return routeMenuItems;
}
