import type { Meta, StoryObj } from "@storybook/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "react-oidc-context";
import ContinuationReportTimeline from "@/components/App/ContinuationReports/ContinuationReportTimeline";
import {
  ContinuationReport,
  CRKeys,
} from "@/models/ContinuationReport";
import { StaffUser } from "@/models/Staff";
import ModalProvider from "@/components/Shared/Modals/ModalProvider";
import SnackBarProvider from "@/components/Shared/Popups/SnackBarProvider";

// Mock data
const mockStaffUser1: StaffUser = {
  id: 1,
  name: "John Doe",
  first_name: "John",
  last_name: "Doe",
  auth_user_guid: "user-123",
  is_active: true,
};

const mockStaffUser2: StaffUser = {
  id: 2,
  name: "Jane Smith",
  first_name: "Jane",
  last_name: "Smith",
  auth_user_guid: "user-456",
  is_active: true,
};

const mockCRKeys: CRKeys[] = [
  {
    id: 1,
    key: "INSP-2024-001",
    key_context: "inspection",
    is_active: true,
  },
  {
    id: 2,
    key: "PROJ-2024-005",
    key_context: "project",
    is_active: true,
  },
];

const mockContinuationReports: ContinuationReport[] = [
  {
    id: 1,
    case_file_id: 123,
    text: "Initial case file created. Project assessment commenced for environmental compliance review.",
    rich_text:
      "<p>Initial case file created. <strong>Project assessment commenced</strong> for environmental compliance review.</p>",
    created_by_user: mockStaffUser1,
    context_type: "case_file",
    context_id: 123,
    system_generated: true,
    date_created: "2024-01-15T09:00:00Z",
    is_active: true,
    keys: [],
  },
  {
    id: 2,
    case_file_id: 123,
    text: "Site inspection scheduled for February 1st. Coordinating with project team and regulatory partners.",
    rich_text:
      "<p>Site inspection scheduled for <em>February 1st</em>. Coordinating with project team and regulatory partners.</p>",
    created_by_user: mockStaffUser1,
    context_type: "inspection",
    context_id: 456,
    system_generated: false,
    date_created: "2024-01-20T14:30:00Z",
    is_active: true,
    keys: mockCRKeys,
  },
  {
    id: 3,
    case_file_id: 123,
    text: "Received additional documentation from proponent. Environmental impact assessment report includes detailed mitigation measures.",
    rich_text:
      "<p>Received additional documentation from proponent. <strong>Environmental impact assessment report</strong> includes detailed mitigation measures.</p><ul><li>Water quality monitoring plan</li><li>Wildlife habitat protection measures</li><li>Air quality management strategy</li></ul>",
    created_by_user: mockStaffUser2,
    context_type: "document",
    context_id: 789,
    system_generated: false,
    date_created: "2024-01-25T11:15:00Z",
    is_active: true,
    keys: [],
  },
  {
    id: 4,
    case_file_id: 123,
    text: "Inspection completed. Several non-compliance issues identified requiring immediate attention.",
    rich_text:
      "<p><strong>Inspection completed.</strong> Several non-compliance issues identified requiring immediate attention:</p><ol><li>Improper waste storage containers</li><li>Missing spill containment measures</li><li>Inadequate erosion control barriers</li></ol><p>Follow-up inspection scheduled for next month.</p>",
    created_by_user: mockStaffUser1,
    context_type: "inspection",
    context_id: 456,
    system_generated: false,
    date_created: "2024-02-01T16:45:00Z",
    is_active: true,
    keys: mockCRKeys,
  },
  {
    id: 5,
    case_file_id: 123,
    text: "Enforcement action initiated. Notice of violation issued to proponent.",
    rich_text:
      "<p><strong>Enforcement action initiated.</strong> Notice of violation issued to proponent.</p>",
    created_by_user: undefined,
    context_type: "enforcement",
    context_id: 101,
    system_generated: true,
    date_created: "2024-02-05T13:20:00Z",
    is_active: true,
    keys: [],
  },
];

// Mock auth configuration
const mockAuthConfig = {
  authority: "https://mock-auth.example.com",
  client_id: "mock-client",
  redirect_uri: "http://localhost:3000",
  response_type: "code",
};

// Wrapper component to provide necessary context
const ContinuationReportTimelineWrapper = ({
  crtList = mockContinuationReports,
  searchText,
  isAllowEdit = false,
}: {
  crtList?: ContinuationReport[];
  searchText?: string;
  isAllowEdit?: boolean;
}) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: 5 * 60 * 1000, // 5 minutes
      },
    },
  });

  return (
    <AuthProvider {...mockAuthConfig}>
      <QueryClientProvider client={queryClient}>
        <SnackBarProvider />
        <ModalProvider />
        <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
          <ContinuationReportTimeline
            crtList={crtList}
            searchText={searchText}
            isAllowEdit={isAllowEdit}
          />
        </div>
      </QueryClientProvider>
    </AuthProvider>
  );
};

const meta: Meta<typeof ContinuationReportTimelineWrapper> = {
  title: "App/ContinuationReports/ContinuationReportTimeline",
  component: ContinuationReportTimelineWrapper,
  parameters: {
    layout: "fullscreen",
    docs: {
      description: {
        component: `
# ContinuationReportTimeline Component

The ContinuationReportTimeline component displays a chronological timeline of continuation report entries for a case file. It provides a visual representation of the case progression with timestamps, user information, and rich text content.

## Features

- **Timeline Display**: Shows entries in chronological order with timestamps
- **Rich Text Support**: Renders HTML content with proper formatting
- **User Attribution**: Displays creator information for manual entries
- **System Generated Entries**: Distinguishes between manual and system-generated entries
- **Search Highlighting**: Highlights search terms within entry content
- **Edit Permissions**: Allows authorized users to edit their own entries
- **Navigation Links**: Converts context keys into clickable navigation links
- **Responsive Design**: Adapts to different screen sizes

## Entry Types

- **System Generated**: Automatically created entries (e.g., case file creation, status changes)
- **Manual Entries**: User-created entries with attribution and edit capabilities
- **Contextual Links**: Entries can reference other entities like inspections, projects, etc.

## Permissions

- Users can edit their own manual entries
- Superusers can edit any manual entry
- System-generated entries cannot be edited
- Edit functionality requires \`isAllowEdit\` prop to be true

## Usage

The component integrates with the modal system for editing entries and uses the snackbar for user notifications. It requires authentication context for user identification and permission checking.
        `,
      },
    },
  },
  tags: ["autodocs"],
  argTypes: {
    crtList: {
      control: "object",
      description:
        "Array of continuation report entries to display in the timeline",
    },
    searchText: {
      control: "text",
      description: "Text to highlight within the timeline entries",
    },
    isAllowEdit: {
      control: "boolean",
      description:
        "Whether to allow editing of entries (requires proper permissions)",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    crtList: mockContinuationReports,
    isAllowEdit: false,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Default timeline view showing a mix of system-generated and manual entries in chronological order.",
      },
    },
  },
};

export const WithEditPermissions: Story = {
  args: {
    crtList: mockContinuationReports,
    isAllowEdit: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Timeline with edit permissions enabled. Manual entries become clickable for authorized users.",
      },
    },
  },
};

export const WithSearchHighlighting: Story = {
  args: {
    crtList: mockContinuationReports,
    searchText: "inspection",
    isAllowEdit: false,
  },
  parameters: {
    docs: {
      description: {
        story:
          'Timeline with search text highlighting. The search term "inspection" is highlighted in yellow throughout the entries.',
      },
    },
  },
};

export const SystemGeneratedOnly: Story = {
  args: {
    crtList: mockContinuationReports.filter(
      (report) => report.system_generated
    ),
    isAllowEdit: false,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Timeline showing only system-generated entries. These entries do not show user attribution and cannot be edited.",
      },
    },
  },
};

export const ManualEntriesOnly: Story = {
  args: {
    crtList: mockContinuationReports.filter(
      (report) => !report.system_generated
    ),
    isAllowEdit: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Timeline showing only manual entries created by users. Each entry shows the creator and can be edited by authorized users.",
      },
    },
  },
};

export const SingleEntry: Story = {
  args: {
    crtList: [mockContinuationReports[2]], // The detailed documentation entry
    isAllowEdit: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Timeline with a single detailed entry showing rich text formatting with lists and emphasis.",
      },
    },
  },
};

export const EmptyTimeline: Story = {
  args: {
    crtList: [],
    isAllowEdit: false,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Empty timeline state when no continuation report entries exist.",
      },
    },
  },
};

export const LongContent: Story = {
  args: {
    crtList: [
      {
        id: 100,
        case_file_id: 123,
        text: "Extended entry with very long content to demonstrate the read more functionality.",
        rich_text: `
          <p><strong>Comprehensive Environmental Assessment Report</strong></p>
          <p>This detailed assessment covers multiple environmental factors and compliance requirements for the proposed project. The following sections provide an in-depth analysis of potential impacts and mitigation strategies.</p>
          
          <h3>Air Quality Assessment</h3>
          <p>The air quality impact assessment evaluated potential emissions from construction and operational phases. Key findings include:</p>
          <ul>
            <li>Construction phase dust generation within acceptable limits</li>
            <li>Operational emissions below regulatory thresholds</li>
            <li>Recommended monitoring protocols for ongoing compliance</li>
          </ul>
          
          <h3>Water Resources Impact</h3>
          <p>Comprehensive evaluation of surface water and groundwater impacts revealed:</p>
          <ul>
            <li>Minimal impact on existing water quality</li>
            <li>Proposed stormwater management system meets requirements</li>
            <li>Groundwater monitoring wells to be established</li>
          </ul>
          
          <h3>Wildlife and Habitat Considerations</h3>
          <p>The biological assessment identified several species of concern and recommended protection measures:</p>
          <ol>
            <li>Seasonal construction restrictions during breeding periods</li>
            <li>Habitat compensation areas to be established</li>
            <li>Wildlife corridor maintenance requirements</li>
            <li>Long-term monitoring and adaptive management protocols</li>
          </ol>
          
          <p>Additional consultation with First Nations communities and stakeholders is ongoing to ensure all concerns are adequately addressed in the final project design.</p>
        `,
        created_by_user: mockStaffUser2,
        context_type: "assessment",
        context_id: 999,
        system_generated: false,
        date_created: "2024-02-10T10:30:00Z",
        is_active: true,
        keys: [],
      },
    ],
    isAllowEdit: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Timeline entry with extensive content demonstrating the read more/less functionality for long entries.",
      },
    },
  },
};

export const WithContextualLinks: Story = {
  args: {
    crtList: [
      {
        id: 200,
        case_file_id: 123,
        text: "Referenced inspection INSP-2024-001 and project PROJ-2024-005 in this entry.",
        rich_text:
          "<p>Referenced inspection <strong>INSP-2024-001</strong> and project <strong>PROJ-2024-005</strong> in this entry. These links will be automatically converted to navigation links.</p>",
        created_by_user: mockStaffUser1,
        context_type: "reference",
        context_id: 555,
        system_generated: false,
        date_created: "2024-02-12T09:15:00Z",
        is_active: true,
        keys: mockCRKeys,
      },
    ],
    isAllowEdit: true,
  },
  parameters: {
    docs: {
      description: {
        story:
          "Timeline entry demonstrating contextual links functionality where referenced entities become clickable navigation links.",
      },
    },
  },
};
