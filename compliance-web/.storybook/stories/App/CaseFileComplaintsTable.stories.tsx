import type { Meta, StoryObj } from "@storybook/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Box } from "@mui/material";
import CaseFileComplaintsTable from "@/components/App/CaseFiles/Profile/CaseFileComplaintsTable";
import { CaseFile } from "@/models/CaseFile";
import { Complaint } from "@/models/Complaint";
import { Initiation } from "@/models/Initiation";
import { Project } from "@/models/Project";
import { StaffUser } from "@/models/Staff";
import { ComplaintSource } from "@/models/ComplaintSource";
import { RequirementSource } from "@/models/RequirementSource";
import { Contact } from "@/models/Contact";
import { Topic } from "@/models/Topic";
import { ComplaintResolution } from "@/models/ComplaintResolution";
import { Agency } from "@/models/Agency";
import { INITIATION } from "@/utils/constants";
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

  const complaintsRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/ce-database/complaints/$complaintNumber",
    component: () => <div />,
  });

  const indexRoute = createRoute({
    getParentRoute: () => rootRoute,
    path: "/",
    component: () => <>{children}</>,
  });

  const routeTree = rootRoute.addChildren([indexRoute, complaintsRoute]);

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

// Create a query client for stories
const createQueryClientWithData = (
  complaints: Complaint[],
  caseFileId: number
) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: Infinity,
      },
    },
  });

  // Pre-populate the query cache with mock data
  queryClient.setQueryData(["complaints-by-caseFileId", caseFileId], {
    items: complaints,
    total: complaints.length,
  });

  return queryClient;
};

// Mock data
const mockStaffUser: StaffUser = {
  id: 1,
  name: "John Smith",
  first_name: "John",
  last_name: "Smith",
  is_active: true,
};

const mockInitiation: Initiation = {
  id: INITIATION.COMPLAINTS_ID,
  name: "Complaints",
};

const mockProject: Project = {
  id: 1,
  name: "Sample Environmental Project",
  abbreviation: "SEP",
  description: "A sample project for testing",
  is_active: true,
  type: {
    id: 1,
    name: "Environmental Assessment",
    short_name: "EA",
    is_active: true,
    sort_order: 1,
  },
  sub_type: {
    id: 1,
    name: "Major Project",
    short_name: "Major",
    is_active: true,
    sort_order: 1,
  },
};

const mockComplaintSource: ComplaintSource = {
  id: "1",
  name: "Public",
};

const mockRequirementSource: RequirementSource = {
  id: "1",
  name: "Environmental Assessment Certificate",
  source_title: "EAC Requirements",
};

const mockContact: Contact = {
  full_name: "Jane Doe",
  email: "jane.doe@example.com",
  phone: "(555) 123-4567",
};

const mockTopic: Topic = {
  id: 1,
  name: "Air Quality",
  is_active: true,
};

const mockComplaintResolution: ComplaintResolution = {
  id: "1",
  name: "Resolved - No Action Required",
};

const mockAgency: Agency = {
  id: 1,
  name: "Environmental Assessment Office",
  abbreviation: "EAO",
  is_active: true,
};

const mockCaseFile: CaseFile = {
  id: 1,
  project_id: 1,
  date_created: "2024-01-15",
  primary_officer_id: 1,
  case_file_number: "CF-2024-001",
  case_file_status: "Active",
  initiation: mockInitiation,
  is_active: true,
  project: mockProject,
  primary_officer: mockStaffUser,
};

const mockComplaint1: Complaint = {
  id: 1,
  complaint_number: "COMP-2024-001",
  case_file_id: 1,
  project_id: 1,
  project_description: "Sample Environmental Project",
  concern_description:
    "Excessive noise during construction activities disturbing nearby residents. The construction work appears to be happening outside permitted hours.",
  location_description: "123 Main Street, Vancouver, BC",
  primary_officer_id: 1,
  date_received: "2024-01-10",
  topic_id: 1,
  requirement_source_id: 1,
  requirement_source_description:
    "Environmental Assessment Certificate Condition 12",
  source_type_id: 1,
  source_agency_id: 1,
  source_first_nation_id: 0,
  is_active: true,
  case_file: mockCaseFile,
  primary_officer: mockStaffUser,
  project: mockProject,
  topic: mockTopic,
  source_type: mockComplaintSource,
  requirement_source: mockRequirementSource,
  source_contact: mockContact,
  requirement_detail: {
    id: 1,
    complaint_id: 1,
    order_number: "ORDER-001",
  },
  status: "Open",
  resolution: mockComplaintResolution,
  resolution_agency: mockAgency,
};

const mockComplaint2: Complaint = {
  id: 2,
  complaint_number: "COMP-2024-002",
  case_file_id: 1,
  project_id: 1,
  project_description: "Sample Environmental Project",
  concern_description:
    "Potential water contamination from construction runoff affecting local stream quality.",
  location_description: "Near Salmon Creek, Richmond, BC",
  primary_officer_id: 1,
  date_received: "2024-01-20",
  topic_id: 1,
  requirement_source_id: 1,
  source_type_id: 1,
  source_agency_id: 1,
  source_first_nation_id: 0,
  is_active: true,
  case_file: mockCaseFile,
  primary_officer: mockStaffUser,
  project: mockProject,
  topic: mockTopic,
  source_type: mockComplaintSource,
  requirement_source: mockRequirementSource,
  source_contact: mockContact,
  requirement_detail: {
    id: 2,
    complaint_id: 2,
    order_number: "ORDER-002",
  },
  status: "Closed",
};

const mockComplaint3: Complaint = {
  id: 3,
  complaint_number: "COMP-2024-003",
  case_file_id: 1,
  project_id: 1,
  project_description: "Sample Environmental Project",
  concern_description:
    "Dust emissions from construction site affecting air quality in residential area.",
  location_description: "456 Oak Avenue, Burnaby, BC",
  primary_officer_id: 1,
  date_received: "2024-02-01",
  topic_id: 1,
  requirement_source_id: 1,
  source_type_id: 1,
  source_agency_id: 1,
  source_first_nation_id: 0,
  is_active: true,
  case_file: mockCaseFile,
  primary_officer: {
    ...mockStaffUser,
    id: 2,
    name: "Sarah Johnson",
    first_name: "Sarah",
    last_name: "Johnson",
  },
  project: mockProject,
  topic: mockTopic,
  source_type: mockComplaintSource,
  requirement_source: mockRequirementSource,
  source_contact: mockContact,
  requirement_detail: {
    id: 3,
    complaint_id: 3,
    order_number: "ORDER-003",
  },
  status: "Open",
};

const meta: Meta<typeof CaseFileComplaintsTable> = {
  title: "App/CaseFiles/CaseFileComplaintsAccordion",
  component: CaseFileComplaintsTable,
  parameters: {
    layout: "padded",
  },
  decorators: [
    (Story, context) => {
      // Get mock data and case file from story context
      const complaints = context.parameters?.mockComplaints || [];
      const caseFileId = context.args?.caseFile?.id || 1;

      // Create a query client with pre-populated data
      const queryClient = createQueryClientWithData(complaints, caseFileId);

      return (
        <QueryClientProvider client={queryClient}>
          <StorybookRouterProvider>
            <Box sx={{ maxWidth: "800px", margin: "0 auto" }}>
              <Story />
            </Box>
          </StorybookRouterProvider>
        </QueryClientProvider>
      );
    },
  ],
  tags: ["autodocs"],
  argTypes: {
    caseFile: {
      control: "object",
      description: "The case file data containing initiation information",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const WithComplaints: Story = {
  args: {
    caseFile: mockCaseFile,
  },
  parameters: {
    mockComplaints: [mockComplaint1, mockComplaint2, mockComplaint3],
  },
};

export const WithSingleComplaint: Story = {
  args: {
    caseFile: mockCaseFile,
  },
  parameters: {
    mockComplaints: [mockComplaint1],
  },
};
