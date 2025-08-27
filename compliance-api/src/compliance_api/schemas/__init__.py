# Copyright © 2024 Province of British Columbia
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Exposes all of the schemas in the compliance_api."""
from .administrative_penalty import (
    AdministrativePenaltyCreateSchema, AdministrativePenaltySchema, AdministrativePenaltyUpdateSchema, DecisionSchema,
    ReferralStatusSchema)
from .agency import AgencyCreateSchema, AgencySchema
from .appendix import AppendixCreateSchema, AppendixSchema
from .case_file import (
    CaseFileCreateSchema, CaseFileFilterSchema, CaseFileLinkCreateSchema, CaseFileLinkSchema, CaseFileOfficerSchema,
    CaseFileOptionSchema, CaseFileSchema, CaseFileStatusSchema, CaseFileUnlinkSchema, CaseFileUpdateSchema)
from .common import KeyValueSchema
from .complaint import (
    ComplaintCreateSchema, ComplaintFilterSchema, ComplaintSchema, ComplaintSourceContactSchema, ComplaintStatusSchema,
    ComplaintUpdateSchema, RequirementSourceDetailSchema)
from .continuation_report import (
    ContinuationReportCreateSchema, ContinuationReportKeyCreateSchema, ContinuationReportKeySchema,
    ContinuationReportSchema, ContinuationReportUpdateSchema, CRGetQueryParamSchema)
from .department_detail import DepartmentDetailsSchema
from .inspection import (
    InspectionAttendanceSchema, InspectionCreateSchema, InspectionFilterSchema, InspectionMoreDetailsSchema,
    InspectionOfficerSchema, InspectionSchema, InspectionStatusSchema, InspectionUpdateSchema)
from .inspection_approval import (
    CreateInspectionRecordApprovalSchema, InspectionRecordApprovalSchema, UpdateInspectionRecordApprovalSchema,
    UpdateInspectionRecordApprovalStatusSchema)
from .inspection_record import (
    InspectionRecordCreateSchema, InspectionRecordSchema, ResetInspectionRecordFieldSchema,
    UpdateInspectionRecordSchema)
from .inspection_record_preview import InspectionRecordPreviewSchema
from .inspection_requirement import (
    InspectionReqImageCreateSchema, InspectionReqImageSchema, InspectionReqImageSortOrderSchema,
    InspectionRequirementBulkUpdateSchema, InspectionRequirementCreateSchema, InspectionRequirementSchema,
    InspectionRequirementUpdateSchema, InspectionSortOrderSchema)
from .inspection_requirement_grid import InspectionRequirementFilterSchema, InspectionRequirementGridItemSchema
from .order import (
    OrderCreateSchema, OrderIssueSchema, OrderReplaceSchema, OrderSchema, OrderStatusSchema, OrderUpdateSchema,
    ResetOrderFieldSchema)
from .order_approval import CreateOrderApprovalSchema, OrderApprovalSchema, UpdateOrderApprovalStatusSchema
from .paginate import PaginationParameterSchema
from .project import ProjectSchema
from .requirement_source import RequirementSourceSchema
from .section import SectionSchema
from .staff_user import StaffUserCreateSchema, StaffUserSchema, StaffUserUpdateSchema
from .topic import TopicCreateSchema, TopicSchema
from .warning_letter import (
    ResetWarningLetterFieldSchema, WarningLetterCreateSchema, WarningLetterIssueSchema, WarningLetterSchema,
    WarningLetterStatusSchema, WarningLetterUpdateSchema)
from .warning_letter_approval import (
    CreateWarningLetterApprovalSchema, UpdateWarningLetterApprovalStatusSchema, WarningLetterApprovalSchema)
