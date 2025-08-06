/// <reference types="cypress" />
import { ComplaintFormSchema, formatComplaintData, ComplaintSourceEnum } from "@/components/App/Complaints/ComplaintFormUtils";
import { RequirementSourceEnum } from "@/utils/constants";
import dayjs from "dayjs";

describe("ComplaintFormUtils", () => {
  describe("ComplaintFormSchema Validation", () => {
    it("validates successfully with correct data", () => {
      const validData = {
        concernDescription: "Test concern description",
        locationDescription: "Test location",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs(),
        complaintSource: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
        contactFullName: "Jane Smith",
        contactEmail: "jane.smith@example.com",
        contactPhoneNumber: "250-123-4567",
        contactComments: "Test comments",
        agency: { id: 1, name: "Test Agency" },
        requirementSource: { id: RequirementSourceEnum.SCHEDULE_B, name: "Schedule B" },
        conditionNumber: "C-123",
        topic: { id: 1, name: "Test Topic" }
      };

      ComplaintFormSchema.validate(validData).then((validatedData) => {
        expect(validatedData).to.deep.equal(validData);
      });
    });

    it("fails validation when required fields are missing", () => {
      const invalidData = {
        concernDescription: null,
        primaryOfficer: null,
        dateReceived: null,
        complaintSource: null
      };

      ComplaintFormSchema.validate(invalidData).catch((err) => {
        expect(err.errors).to.include("Concern Description is required");
        expect(err.errors).to.include("Primary is required");
        expect(err.errors).to.include("Date Received is required");
        expect(err.errors).to.include("Complaint Source is required");
      });
    });

    it("validates email format correctly", () => {
      const invalidEmail = {
        concernDescription: "Test concern",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs(),
        complaintSource: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
        contactEmail: "invalid-email",
        agency: { id: 1, name: "Test Agency" }
      };

      ComplaintFormSchema.validate(invalidEmail).catch((err) => {
        expect(err.errors).to.include("Invalid email format");
      });
    });

    it("validates phone number format correctly", () => {
      const invalidPhone = {
        concernDescription: "Test concern",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs(),
        complaintSource: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
        contactPhoneNumber: "123",
        agency: { id: 1, name: "Test Agency" }
      };

      ComplaintFormSchema.validate(invalidPhone).catch((err) => {
        expect(err.errors).to.include("Invalid phone number format");
      });
    });

    it("validates conditional fields based on complaint source", () => {
      // Test Agency source requires agency field
      const agencySourceMissingAgency = {
        concernDescription: "Test concern",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs(),
        complaintSource: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
        agency: null
      };

      ComplaintFormSchema.validate(agencySourceMissingAgency).catch((err) => {
        expect(err.errors).to.include("Agency is required");
      });

      // Test First Nation source requires firstNation field
      const firstNationSourceMissingFirstNation = {
        concernDescription: "Test concern",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs(),
        complaintSource: { id: ComplaintSourceEnum.FIRST_NATION, name: "First Nation" },
        firstNation: null
      };

      ComplaintFormSchema.validate(firstNationSourceMissingFirstNation).catch((err) => {
        expect(err.errors).to.include("First Nation is required");
      });

      // Test Other source requires otherDescription field
      const otherSourceMissingDescription = {
        concernDescription: "Test concern",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs(),
        complaintSource: { id: ComplaintSourceEnum.OTHER, name: "Other" },
        otherDescription: null
      };

      ComplaintFormSchema.validate(otherSourceMissingDescription).catch((err) => {
        expect(err.errors).to.include("Description is required");
      });
    });

    it("validates conditional fields based on requirement source", () => {
      // Test Schedule B requires conditionNumber
      const scheduleBMissingConditionNumber = {
        concernDescription: "Test concern",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs(),
        complaintSource: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
        agency: { id: 1, name: "Test Agency" },
        requirementSource: { id: RequirementSourceEnum.SCHEDULE_B, name: "Schedule B" },
        conditionNumber: null,
        topic: { id: 1, name: "Test Topic" }
      };

      ComplaintFormSchema.validate(scheduleBMissingConditionNumber).catch((err) => {
        expect(err.errors).to.include("Condition Number is required");
      });

      // Test requirement source requires topic
      const requirementSourceMissingTopic = {
        concernDescription: "Test concern",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs(),
        complaintSource: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
        agency: { id: 1, name: "Test Agency" },
        requirementSource: { id: RequirementSourceEnum.ACT2018, name: "Act 2018" },
        topic: null
      };

      ComplaintFormSchema.validate(requirementSourceMissingTopic).catch((err) => {
        expect(err.errors).to.include("Topic is required");
      });
    });
  });

  describe("formatComplaintData function", () => {
    it("formats data correctly for API submission with Agency source", () => {
      const formData = {
        concernDescription: "Test concern description",
        locationDescription: "Test location",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs("2023-01-01"),
        complaintSource: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
        contactFullName: "Jane Smith",
        contactEmail: "jane.smith@example.com",
        contactPhoneNumber: "250-123-4567",
        contactComments: "Test comments",
        agency: { id: 2, name: "Test Agency" },
        requirementSource: { id: RequirementSourceEnum.SCHEDULE_B, name: "Schedule B" },
        requirementSourceDescription: "Test requirement description",
        topic: { id: 3, name: "Test Topic" }
      };

      const expectedFormattedData = {
        primary_officer_id: 1,
        location_description: "Test location",
        concern_description: "Test concern description",
        topic_id: 3,
        date_received: dayjs("2023-01-01").toISOString(),
        source_type_id: ComplaintSourceEnum.AGENCY,
        requirement_source_id: RequirementSourceEnum.SCHEDULE_B,
        complaint_source_contact: {
          full_name: "Jane Smith",
          email: "jane.smith@example.com",
          phone: "250-123-4567",
          comment: "Test comments"
        },
        source_agency_id: 2,
        requirement_source_description: "Test requirement description",
        case_file_id: 123
      };

      const formattedData = formatComplaintData(formData, 123);
      expect(formattedData).to.deep.equal(expectedFormattedData);
    });

    it("formats data correctly for API submission with First Nation source", () => {
      const formData = {
        concernDescription: "Test concern description",
        locationDescription: "Test location",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs("2023-01-01"),
        complaintSource: { id: ComplaintSourceEnum.FIRST_NATION, name: "First Nation" },
        contactFullName: "Jane Smith",
        contactEmail: "jane.smith@example.com",
        contactPhoneNumber: "250-123-4567",
        contactComments: "Test comments",
        firstNation: { id: 2, name: "Test First Nation" },
        requirementSource: { id: RequirementSourceEnum.EAC, name: "EAC" },
        requirementSourceDescription: "Test requirement description",
        topic: { id: 3, name: "Test Topic" }
      };

      const expectedFormattedData = {
        primary_officer_id: 1,
        location_description: "Test location",
        concern_description: "Test concern description",
        topic_id: 3,
        date_received: dayjs("2023-01-01").toISOString(),
        source_type_id: ComplaintSourceEnum.FIRST_NATION,
        requirement_source_id: RequirementSourceEnum.EAC,
        complaint_source_contact: {
          full_name: "Jane Smith",
          email: "jane.smith@example.com",
          phone: "250-123-4567",
          comment: "Test comments"
        },
        source_first_nation_id: 2,
        requirement_source_description: "Test requirement description",
        case_file_id: undefined
      };

      const formattedData = formatComplaintData(formData);
      expect(formattedData).to.deep.equal(expectedFormattedData);
    });

    it("formats data correctly for API submission with Other source", () => {
      const formData = {
        concernDescription: "Test concern description",
        locationDescription: "Test location",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs("2023-01-01"),
        complaintSource: { id: ComplaintSourceEnum.OTHER, name: "Other" },
        contactFullName: "Jane Smith",
        contactEmail: "jane.smith@example.com",
        contactPhoneNumber: "250-123-4567",
        contactComments: "Test comments",
        otherDescription: "Other source description",
        requirementSource: { id: RequirementSourceEnum.OTHER, name: "Other" },
        requirementSourceDescription: "Test requirement description",
        topic: { id: 3, name: "Test Topic" }
      };

      const expectedFormattedData = {
        primary_officer_id: 1,
        location_description: "Test location",
        concern_description: "Test concern description",
        topic_id: 3,
        date_received: dayjs("2023-01-01").toISOString(),
        source_type_id: ComplaintSourceEnum.OTHER,
        requirement_source_id: RequirementSourceEnum.OTHER,
        complaint_source_contact: {
          full_name: "Jane Smith",
          email: "jane.smith@example.com",
          phone: "250-123-4567",
          comment: "Test comments",
          description: "Other source description"
        },
        requirement_source_description: "Test requirement description",
        case_file_id: undefined
      };

      const formattedData = formatComplaintData(formData);
      expect(formattedData).to.deep.equal(expectedFormattedData);
    });

    it("formats data correctly for API submission with Order requirement source", () => {
      const formData = {
        concernDescription: "Test concern description",
        locationDescription: "Test location",
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs("2023-01-01"),
        complaintSource: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
        contactFullName: "Jane Smith",
        contactEmail: "jane.smith@example.com",
        contactPhoneNumber: "250-123-4567",
        contactComments: "Test comments",
        agency: { id: 2, name: "Test Agency" },
        requirementSource: { id: RequirementSourceEnum.ORDER, name: "Order" },
        order: { id: 1, order_number: "ORD-001" },
        topic: { id: 3, name: "Test Topic" }
      };

      const expectedFormattedData = {
        primary_officer_id: 1,
        location_description: "Test location",
        concern_description: "Test concern description",
        topic_id: 3,
        date_received: dayjs("2023-01-01").toISOString(),
        source_type_id: ComplaintSourceEnum.AGENCY,
        requirement_source_id: RequirementSourceEnum.ORDER,
        complaint_source_contact: {
          full_name: "Jane Smith",
          email: "jane.smith@example.com",
          phone: "250-123-4567",
          comment: "Test comments"
        },
        source_agency_id: 2,
        requirement_source_details: {
          order_number: "ORD-001"
        },
        case_file_id: 123
      };

      const formattedData = formatComplaintData(formData, 123);
      expect(formattedData).to.deep.equal(expectedFormattedData);
    });

    it("handles null values correctly", () => {
      const formData = {
        concernDescription: "Test concern description",
        locationDescription: null,
        primaryOfficer: { id: 1, full_name: "John Doe" },
        dateReceived: dayjs("2023-01-01"),
        complaintSource: { id: ComplaintSourceEnum.AGENCY, name: "Agency" },
        contactFullName: null,
        contactEmail: null,
        contactPhoneNumber: null,
        contactComments: null,
        agency: { id: 2, name: "Test Agency" },
        requirementSource: null
      };

      const expectedFormattedData = {
        primary_officer_id: 1,
        location_description: "",
        concern_description: "Test concern description",
        topic_id: undefined,
        date_received: dayjs("2023-01-01").toISOString(),
        source_type_id: ComplaintSourceEnum.AGENCY,
        requirement_source_id: undefined,
        complaint_source_contact: {
          full_name: "",
          email: "",
          phone: "",
          comment: ""
        },
        source_agency_id: 2,
        case_file_id: undefined
      };

      const formattedData = formatComplaintData(formData);
      expect(formattedData).to.deep.equal(expectedFormattedData);
    });
  });
});
