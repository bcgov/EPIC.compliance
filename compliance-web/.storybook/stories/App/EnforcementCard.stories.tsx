import type { Meta, StoryObj } from "@storybook/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Box } from "@mui/material";
import EnforcementCard from "@/components/App/Inspections/Profile/Enforcements/EnforcementCard";
import type { InspectionOrder } from "@/models/InspectionOrder";
import type { InspectionWarningLetter } from "@/models/InspectionWarningLetter";
import type { AdministrativePenalty } from "@/models/AdministrativePenalty";
import type { ChargeRecommendation } from "@/models/ChargeRecommendation";
import type { ViolationTicket } from "@/models/ViolationTicket";
import type { RestorativeJustice } from "@/models/RestorativeJustice";
import type { InspectionRequirement } from "@/models/InspectionRequirement";
import type { InspectionRequirementType } from "@/models/InspectionRequirementType";
import type { Topic } from "@/models/Topic";
import type { Agency } from "@/models/Agency";
import type { ComplianceFinding } from "@/models/ComplianceFinding";
import type { StaffUser } from "@/models/Staff";
import type { Option } from "@/models/common";
import type { OrderApproval } from "@/models/OrderApproval";
import type { WarningLetterApproval } from "@/models/WarningLetterApproval";
import type { ApprovalStatus } from "@/models/ApprovalStatus";

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
const mockStaffUser: StaffUser = {
  id: 1,
  name: "John Smith",
  first_name: "John",
  last_name: "Smith",
  position_id: 3,
  position: {
    id: "3",
    name: "Deputy Director",
  },
  is_active: true,
};

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

const mockRequirementType: InspectionRequirementType = {
  id: "1",
  name: "Requirement",
};

const mockInspectionRequirement: InspectionRequirement = {
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
  enforcement_action_data: [],
  findings:
    "<p>The monitoring equipment was found to be non-functional during the inspection.</p>",
  sort_order: 1,
  is_active: true,
  requirement_source_details: [],
};

const mockOption: Option = {
  id: "1",
  name: "Approved",
};

const mockDecisionOption: Option = {
  id: "1",
  name: "Penalty Imposed",
};

const mockChargeDecisionOption: Option = {
  id: "1",
  name: "Charges Approved",
};

const mockJudgmentOption: Option = {
  id: "1",
  name: "Guilty",
};

const mockApprovalStatus: ApprovalStatus = {
  id: "1",
  name: "Approved",
};

// Mock Inspection Order
const mockInspectionOrder: InspectionOrder = {
  id: 1,
  order_number: "ORD-2024-001",
  inspection_id: 123,
  where_as: "Environmental compliance requirements not being met",
  now_therefore:
    "The following actions are required to be completed immediately",
  date_issued: "2024-03-15",
  intended_issuance_date: "2024-03-10",
  issuing_officer_id: 1,
  issuing_officer: mockStaffUser,
  section_id: 1,
  section: {
    id: 1,
    name: "Section 36(1)",
  },
  order_status: mockOption,
  order_progress: mockOption,
  is_active: true,
  order_approvals: [
    {
      id: 1,
      order_id: 1,
      approved_by_id: 1,
      approved_by: mockStaffUser,
      approved_date: "2024-03-14",
      created_date: "2024-03-14",
      approval_status: mockApprovalStatus,
      order_status: mockOption,
    } as OrderApproval,
  ],
};

// Mock Warning Letter
const mockWarningLetter: InspectionWarningLetter = {
  id: 1,
  warning_letter_number: "WL-2024-001",
  inspection_id: 123,
  content:
    "This warning letter is issued due to non-compliance with environmental regulations.",
  date_issued: "2024-03-10",
  intended_issuance_date: "2024-03-05",
  issuing_officer_id: 1,
  issuing_officer: mockStaffUser,
  is_active: true,
  status: mockOption,
  progress: mockOption,
  warning_letter_approvals: [
    {
      id: 1,
      warning_letter_id: 1,
      approved_by_id: 1,
      approved_by: mockStaffUser,
      approved_date: "2024-03-09",
      created_date: "2024-03-09",
      approval_status: mockApprovalStatus,
    } as WarningLetterApproval,
  ],
};

// Mock Administrative Penalty
const mockAdministrativePenalty: AdministrativePenalty = {
  id: 1,
  inspection_id: 123,
  administrative_penalty_number: "AP-2024-001",
  date_referred: "2024-03-01",
  decision_date: "2024-03-20",
  decision: mockDecisionOption,
  penalty_amount: "50000",
  referral_status: mockOption,
  is_active: true,
  administrative_penalty_requirement_maps: [],
};

// Mock Charge Recommendation
const mockChargeRecommendation: ChargeRecommendation = {
  id: 1,
  inspection_id: 123,
  charge_recommendation_number: "CR-2024-001",
  status: mockOption,
  date_to_crown_counsel: "2024-02-15",
  charge_decision: mockChargeDecisionOption,
  charge_decision_date: "2024-03-01",
  court_file_number: "CF-2024-12345",
  court_decision: mockJudgmentOption,
  court_decision_date: "2024-04-20",
  sentence_date: "2024-05-01",
  sentence_type_mappings: [],
  is_active: true,
  charge_recommendation_requirement_maps: [],
};

// Mock Violation Ticket
const mockViolationTicket: ViolationTicket = {
  id: 1,
  inspection_id: 123,
  vt_number: "VT-2024-001",
  ticket_number: "TKT-123456",
  date_issued: "2024-03-05",
  fine_amount: "2500",
  status: {
    id: "ISSUED",
    name: "Issued",
  },
  status_date: "2024-03-05",
  created_date: "2024-03-05",
  updated_date: "2024-03-05",
  violation_ticket_requirement_maps: [],
};

// Mock Restorative Justice
const mockRestorativeJustice: RestorativeJustice = {
  id: 1,
  inspection_id: 123,
  restorative_justice_number: "RJ-2024-001",
  restitution_details:
    "Community service work to restore damaged environmental areas. Installation of new monitoring equipment and ongoing maintenance for 2 years.",
  date_restitution_complete: "2024-06-15",
  status: {
    id: "1",
    name: "Completed",
  },
  is_active: true,
  created_at: "2024-03-01",
  updated_at: "2024-06-15",
  restorative_justice_requirement_maps: [],
};

const meta: Meta<typeof EnforcementCard> = {
  title: "App/Inspections/EnforcementCard",
  component: EnforcementCard,
  parameters: {
    layout: "padded",
  },
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <Box sx={{ maxWidth: "900px", margin: "0 auto" }}>
          <Story />
        </Box>
      </QueryClientProvider>
    ),
  ],
  tags: ["autodocs"],
  argTypes: {
    order: {
      control: "object",
      description: "Inspection order data",
    },
    warningLetter: {
      control: "object",
      description: "Warning letter data",
    },
    requirementEnforcements: {
      control: "object",
      description:
        "Array of inspection requirements related to the enforcement",
    },
    administrativePenalty: {
      control: "object",
      description: "Administrative penalty data",
    },
    chargeRecommendation: {
      control: "object",
      description: "Charge recommendation data",
    },
    violationTicket: {
      control: "object",
      description: "Violation ticket data",
    },
    restorativeJustice: {
      control: "object",
      description: "Restorative justice data",
    },
  },
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Order: Story = {
  args: {
    order: mockInspectionOrder,
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const WarningLetter: Story = {
  args: {
    warningLetter: mockWarningLetter,
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const AdminPenalty: Story = {
  args: {
    administrativePenalty: mockAdministrativePenalty,
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const ChargeRec: Story = {
  args: {
    chargeRecommendation: mockChargeRecommendation,
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const Ticket: Story = {
  args: {
    violationTicket: mockViolationTicket,
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const RestorativeJust: Story = {
  args: {
    restorativeJustice: mockRestorativeJustice,
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const OrderWithoutDates: Story = {
  args: {
    order: {
      ...mockInspectionOrder,
      date_issued: undefined,
      order_approvals: [],
    },
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const AdministrativePenaltyWithoutPenaltyAmount: Story = {
  args: {
    administrativePenalty: {
      ...mockAdministrativePenalty,
      penalty_amount: undefined,
      decision: undefined,
    },
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const ChargeRecommendationMinimal: Story = {
  args: {
    chargeRecommendation: {
      ...mockChargeRecommendation,
      court_file_number: undefined,
      court_decision: undefined,
      court_decision_date: undefined,
      sentence_date: undefined,
      sentence_type_mappings: [],
    },
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const RestorativeJusticeWithoutCompletionDate: Story = {
  args: {
    restorativeJustice: {
      ...mockRestorativeJustice,
      date_restitution_complete: undefined,
      status: {
        id: "2",
        name: "In Progress",
      },
    },
    requirementEnforcements: [mockInspectionRequirement],
  },
};

export const MultipleRequirements: Story = {
  args: {
    order: mockInspectionOrder,
    requirementEnforcements: [
      mockInspectionRequirement,
      {
        ...mockInspectionRequirement,
        id: 2,
        summary: "Implement water quality monitoring system",
        topic: {
          id: 2,
          name: "Water Quality",
          is_active: true,
        },
      },
      {
        ...mockInspectionRequirement,
        id: 3,
        summary: "Establish wildlife protection measures",
        topic: {
          id: 3,
          name: "Wildlife Protection",
          is_active: true,
        },
      },
    ],
  },
};

export const AllEnforcementTypes: Story = {
  render: () => (
    <QueryClientProvider client={queryClient}>
      <Box
        sx={{
          maxWidth: "900px",
          margin: "0 auto",
          gap: 2,
          display: "flex",
          flexDirection: "column",
        }}
      >
        <EnforcementCard
          order={mockInspectionOrder}
          requirementEnforcements={[mockInspectionRequirement]}
        />
        <EnforcementCard
          warningLetter={mockWarningLetter}
          requirementEnforcements={[mockInspectionRequirement]}
        />
        <EnforcementCard
          administrativePenalty={mockAdministrativePenalty}
          requirementEnforcements={[mockInspectionRequirement]}
        />
        <EnforcementCard
          chargeRecommendation={mockChargeRecommendation}
          requirementEnforcements={[mockInspectionRequirement]}
        />
        <EnforcementCard
          violationTicket={mockViolationTicket}
          requirementEnforcements={[mockInspectionRequirement]}
        />
        <EnforcementCard
          restorativeJustice={mockRestorativeJustice}
          requirementEnforcements={[mockInspectionRequirement]}
        />
      </Box>
    </QueryClientProvider>
  ),
};
