import type { Meta, StoryObj } from "@storybook/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Box } from "@mui/material";
import { Reorder } from "framer-motion";
import RequirementCard from "@/components/App/Inspections/Profile/Requirements/RequirementCard";
import { InspectionRequirement } from "@/models/InspectionRequirement";
import { InspectionRequirementType } from "@/models/InspectionRequirementType";
import { Topic } from "@/models/Topic";
import { Agency } from "@/models/Agency";
import { ComplianceFinding } from "@/models/ComplianceFinding";
import { EnforcementAction } from "@/models/EnforcementAction";
import { InspectionRequirementSource } from "@/models/InspectionRequirementSource";
import { RequirementSource } from "@/models/RequirementSource";
import { Appendix } from "@/models/Appendix";
import { InspectionOrder } from "@/models/InspectionOrder";
import {
  REQUIREMENT_TYPE_ID,
  REGULATORY_CONSIDERATION_TYPE_ID,
} from "@/components/App/Inspections/Profile/Requirements/RequirementUtils";

// Create a query client for stories
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      staleTime: Infinity,
    },
  },
});

// Mock data
const mockTopic: Topic = {
  id: 1,
  name: "Air Quality",
  is_active: true,
};

const mockAgency: Agency = {
  id: 1,
  name: "Environmental Assessment Office",
  abbreviation: "EAO",
  is_active: true,
};

const mockComplianceFinding: ComplianceFinding = {
  id: "1",
  name: "Non-Compliant",
};

const mockEnforcementAction: EnforcementAction = {
  id: "1",
  name: "Warning Letter",
};

const mockRequirementType: InspectionRequirementType = {
  id: REQUIREMENT_TYPE_ID,
  name: "Requirement",
};

const mockRegulatoryConsiderationType: InspectionRequirementType = {
  id: REGULATORY_CONSIDERATION_TYPE_ID,
  name: "Regulatory Consideration",
};

const mockRequirementSource: RequirementSource = {
  id: "1",
  name: "Environmental Assessment Act",
  source_title: "Environmental Assessment Act Requirements",
};

const mockAppendix: Appendix = {
  id: 1,
  inspection_id: 123,
  appendix_no: "A",
  document_title: "Appendix A - Environmental Monitoring Requirements",
};

const mockInspectionOrder: InspectionOrder = {
  id: 1,
  order_number: "ORD-2024-001",
  inspection_id: 123,
  where_as: "Environmental compliance requirements",
  now_therefore: "The following actions are required",
  is_active: true,
};

const mockInspectionRequirementSource: InspectionRequirementSource = {
  id: 1,
  requirement_id: 1,
  requirement_source_id: 1,
  requirement_source: mockRequirementSource,
  section_number: "12.1",
  condition_number: "C-001",
  amendment_number: "A-2024-01",
  clause_number: "",
  regulation_number: "R-001",
  compliance_number: "COMP-001",
  source_title: "Environmental Protection Requirements",
  appendix_id: 1,
  appendix: mockAppendix,
  order_id: 1,
  order: mockInspectionOrder,
  title: "Air Quality Monitoring",
  description: "Detailed description of air quality monitoring requirements",
  is_active: true,
  documents: [],
};

const mockRequirement: InspectionRequirement = {
  id: 1,
  req_type: mockRequirementType,
  inspection_id: 123,
  summary:
    "Ensure proper air quality monitoring equipment is installed and operational",
  topic_id: 1,
  topic: mockTopic,
  agency_id: 1,
  agency: mockAgency,
  enforcement_action_id: 1,
  compliance_finding_id: 1,
  compliance_finding: mockComplianceFinding,
  enforcement_action_data: [mockEnforcementAction],
  findings:
    "<p>The monitoring equipment was found to be non-functional during the inspection. <strong>Immediate action required</strong> to bring the equipment back online.</p>",
  sort_order: 1,
  is_active: true,
  requirement_source_details: [mockInspectionRequirementSource],
};

const mockRegulatoryConsideration: InspectionRequirement = {
  ...mockRequirement,
  id: 2,
  req_type: mockRegulatoryConsiderationType,
  summary: "Review regulatory compliance for new environmental standards",
  findings:
    "<p>New environmental standards have been introduced that may affect current operations. <em>Regulatory review recommended</em>.</p>",
  requirement_source_details: [],
};

const mockLongSummaryRequirement: InspectionRequirement = {
  ...mockRequirement,
  id: 3,
  summary:
    "This is a very long requirement summary that demonstrates how the component handles extensive text content and wrapping behavior within the card layout structure",
  findings:
    "<p>This requirement has extensive findings that include multiple paragraphs of detailed information about the inspection results, compliance status, and recommended actions for remediation.</p><p>Additional paragraph with more detailed findings and recommendations for follow-up actions.</p>",
};

const meta: Meta<typeof RequirementCard> = {
  title: "App/Inspections/RequirementCard",
  component: RequirementCard,
  parameters: {
    layout: "padded",
  },
  decorators: [
    (Story, context) => {
      const requirement = context.args?.requirement || mockRequirement;
      const isRegulatoryConsideration =
        requirement.req_type?.id === REGULATORY_CONSIDERATION_TYPE_ID;

      return (
        <QueryClientProvider client={queryClient}>
          <Box sx={{ maxWidth: "800px", margin: "0 auto" }}>
            {isRegulatoryConsideration ? (
              <Story />
            ) : (
              <Reorder.Group
                axis="y"
                values={[requirement]}
                onReorder={() => {}}
                style={{ listStyle: "none", padding: 0, margin: 0 }}
              >
                <Story />
              </Reorder.Group>
            )}
          </Box>
        </QueryClientProvider>
      );
    },
  ],
  tags: ["autodocs"],
  argTypes: {
    requirement: {
      control: "object",
      description: "The inspection requirement data",
    },
    index: {
      control: "number",
      description: "The index of the requirement in the list (0-based)",
    },
    isActive: {
      control: "boolean",
      description: "Whether the requirement card is currently active/selected",
    },
    disabled: {
      control: "boolean",
      description: "Whether the requirement card is disabled",
    },
    dragDisabled: {
      control: "boolean",
      description: "Whether dragging is disabled for this card",
    },
    onEdit: {
      action: "onEdit",
      description:
        "Callback function called when the card is clicked for editing",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  args: {
    requirement: mockRequirement,
    index: 0,
    isActive: false,
    disabled: false,
    dragDisabled: false,
    onEdit: () => console.log("Edit requirement"),
  },
};

export const Active: Story = {
  args: {
    requirement: mockRequirement,
    index: 0,
    isActive: true,
    disabled: false,
    dragDisabled: false,
    onEdit: () => console.log("Edit requirement"),
  },
};

export const Disabled: Story = {
  args: {
    requirement: mockRequirement,
    index: 0,
    isActive: false,
    disabled: true,
    dragDisabled: false,
    onEdit: () => console.log("Edit requirement"),
  },
};

export const DragDisabled: Story = {
  args: {
    requirement: mockRequirement,
    index: 0,
    isActive: false,
    disabled: false,
    dragDisabled: true,
    onEdit: () => console.log("Edit requirement"),
  },
};

export const RegulatoryConsideration: Story = {
  args: {
    requirement: mockRegulatoryConsideration,
    index: 0,
    isActive: false,
    disabled: false,
    dragDisabled: false,
    onEdit: () => console.log("Edit regulatory consideration"),
  },
};

export const RegulatoryConsiderationActive: Story = {
  args: {
    requirement: mockRegulatoryConsideration,
    index: 0,
    isActive: true,
    disabled: false,
    dragDisabled: false,
    onEdit: () => console.log("Edit regulatory consideration"),
  },
};

export const LongSummary: Story = {
  args: {
    requirement: mockLongSummaryRequirement,
    index: 2,
    isActive: false,
    disabled: false,
    dragDisabled: false,
    onEdit: () => console.log("Edit requirement with long summary"),
  },
};

export const MultipleRequirements: Story = {
  render: () => {
    const requirements = [
      mockRequirement,
      mockLongSummaryRequirement,
      { ...mockRequirement, id: 4, summary: "Disabled requirement example" },
    ];

    return (
      <QueryClientProvider client={queryClient}>
        <Box sx={{ maxWidth: "800px", margin: "0 auto" }}>
          <Reorder.Group
            axis="y"
            values={requirements}
            onReorder={() => {}}
            style={{ listStyle: "none", padding: 0, margin: 0 }}
          >
            <RequirementCard
              requirement={mockRequirement}
              index={0}
              isActive={true}
              disabled={false}
              dragDisabled={false}
              onEdit={() => console.log("Edit requirement 1")}
            />
            <RequirementCard
              requirement={mockLongSummaryRequirement}
              index={1}
              isActive={false}
              disabled={false}
              dragDisabled={false}
              onEdit={() => console.log("Edit requirement 2")}
            />
            <RequirementCard
              requirement={{
                ...mockRequirement,
                id: 4,
                summary: "Disabled requirement example",
              }}
              index={2}
              isActive={false}
              disabled={true}
              dragDisabled={false}
              onEdit={() => console.log("Edit disabled requirement")}
            />
          </Reorder.Group>

          {/* Regulatory consideration - rendered outside Reorder.Group */}
          <RequirementCard
            requirement={mockRegulatoryConsideration}
            index={3}
            isActive={false}
            disabled={false}
            dragDisabled={false}
            onEdit={() => console.log("Edit regulatory consideration")}
          />
        </Box>
      </QueryClientProvider>
    );
  },
};

export const WithMultipleEnforcementActions: Story = {
  args: {
    requirement: {
      ...mockRequirement,
      enforcement_action_data: [
        mockEnforcementAction,
        { id: "2", name: "Administrative Penalty" },
        { id: "3", name: "Stop Work Order" },
      ],
    },
    index: 0,
    isActive: false,
    disabled: false,
    dragDisabled: false,
    onEdit: () =>
      console.log("Edit requirement with multiple enforcement actions"),
  },
};
