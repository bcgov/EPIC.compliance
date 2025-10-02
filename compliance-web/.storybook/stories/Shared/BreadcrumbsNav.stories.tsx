import type { Meta, StoryObj } from "@storybook/react";
import { Box } from "@mui/material";
import BreadcrumbsNav, {
  BreadcrumbItem,
} from "@/components/Shared/BreadcrumbsNav";
import {
  createRouter,
  RouterProvider,
  createRoute,
  createRootRoute,
} from "@tanstack/react-router";

// Simple router wrapper component for Storybook
const StorybookRouterProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const rootRoute = createRootRoute({
    component: () => <>{children}</>,
  });

  // Create routes that match the breadcrumb navigation paths
  const caseFilesRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/ce-database/case-files",
    component: () => <div>Case Files Page</div>,
  });

  const specificCaseFileRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/ce-database/case-files/$caseFileNumber",
    component: () => <div>Case File Detail Page</div>,
  });

  const complaintsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/ce-database/complaints",
    component: () => <div>Complaints Page</div>,
  });

  const inspectionsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/ce-database/inspections",
    component: () => <div>Inspections Page</div>,
  });

  const dashboardRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/dashboard",
    component: () => <div>Dashboard Page</div>,
  });

  const indexRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/",
    component: () => <>{children}</>,
  });

  const routeTree = rootRoute.addChildren([
    indexRoute,
    caseFilesRoute,
    specificCaseFileRoute,
    complaintsRoute,
    inspectionsRoute,
    dashboardRoute,
  ]);

  const mockAuth = {
    user: null,
    isAuthenticated: false,
    isLoading: false,
    error: null,
  } as any;

  const router = createRouter({
    routeTree,
    context: {
      authentication: mockAuth,
    },
  }) as any;

  return <RouterProvider router={router} />;
};

const shortBreadcrumbs: BreadcrumbItem[] = [
  { label: "Case Files", to: "/ce-database/case-files" },
  { label: "CF-2024-001" },
];

const deepBreadcrumbs: BreadcrumbItem[] = [
  { label: "Dashboard", to: "/dashboard" },
  { label: "CE Database", to: "/ce-database" },
  { label: "Case Files", to: "/ce-database/case-files" },
  { label: "Environmental Assessment", to: "/ce-database/case-files?type=ea" },
  { label: "CF-2024-001" },
];

const singleBreadcrumb: BreadcrumbItem[] = [{ label: "Dashboard" }];

const meta: Meta<typeof BreadcrumbsNav> = {
  title: "Shared/BreadcrumbsNav",
  component: BreadcrumbsNav,
  parameters: {
    layout: "padded",
    docs: {
      description: {
        component:
          "A navigation breadcrumb component that can display either breadcrumb trail or a back-to-case-file link.",
      },
    },
  },
  decorators: [
    (Story) => (
      <StorybookRouterProvider>
        <Box sx={{ padding: "1rem", maxWidth: "800px", margin: "0 auto" }}>
          <Story />
        </Box>
      </StorybookRouterProvider>
    ),
  ],
  tags: ["autodocs"],
  argTypes: {
    items: {
      control: "object",
      description:
        "Array of breadcrumb items with label and optional navigation path",
    },
    caseFileNumber: {
      control: "text",
      description:
        "When provided, shows a 'Back to Case File' link instead of breadcrumbs",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    items: shortBreadcrumbs,
  },
};

export const DeepNavigation: Story = {
  args: {
    items: deepBreadcrumbs,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Shows breadcrumbs with multiple levels of navigation hierarchy.",
      },
    },
  },
};

export const SingleItem: Story = {
  args: {
    items: singleBreadcrumb,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Shows breadcrumbs with only one item (no links, just current page).",
      },
    },
  },
};

export const BackToCaseFile: Story = {
  args: {
    items: [], // Items are ignored when caseFileNumber is provided
    caseFileNumber: "CF-2024-001",
  },
  parameters: {
    docs: {
      description: {
        story:
          "Shows the 'Back to Case File' link mode instead of breadcrumbs.",
      },
    },
  },
};
