"""Factory scenarios for inspection requirement test data."""

from enum import Enum

from compliance_api.models import InspectionRequirementTypeEnum, RequirementSourceEnum


class InspectionRequirementScenario(Enum):
    """Scenario for inspection requirement test data."""

    with_everything = {
        "summary": "requirement summary 4",
        "topic_id": 1,
        "req_type": InspectionRequirementTypeEnum.REG.name,
        "enforcement_action_ids": [1, 7],
        "compliance_finding_id": 1,
        "findings": "requirement finding",
        "photos": [
            {
                "original_file_name": "filename1.jpg",
                "date_taken": "2024-08-29T20:18:55.740Z",
                "taken_by_id": 1,
                "sort_order": 1,
                "caption": "caption 1",
                "relative_url": "compliance/1/inspection/1/requirement_images/filename1.jpg",
            },
            {
                "original_file_name": "filename2.jpg",
                "date_taken": "2024-08-30T20:18:55.740Z",
                "taken_by_id": 1,
                "sort_order": 2,
                "caption": "caption 2",
                "relative_url": "compliance/1/inspection/1/requirement_images/filename2.jpg",
            },
        ],
        "figures": [
            {
                "original_file_name": "filename3.jpg",
                "date_taken": "2024-08-29T20:18:55.740Z",
                "taken_by_id": 1,
                "caption": "caption 1",
                "sort_order": 1,
                "relative_url": "compliance/1/inspection/1/requirement_images/filename3.jpg",
            },
            {
                "original_file_name": "filename4.jpg",
                "date_taken": "2024-08-30T20:18:55.740Z",
                "taken_by_id": 1,
                "caption": "caption 2",
                "sort_order": 2,
                "relative_url": "compliance/1/inspection/1/requirement_images/filename4.jpg",
            },
        ],
        "requirement_source_details": [
            {
                "requirement_source_id": RequirementSourceEnum.ACT_2018.value,
                "section_number": "1.1",
                "condition_number": "",
                "amendment_number": "",
                "title": "detail title",
                "description": "detail description",
                "documents": [
                    {
                        "document_type_id": 1,
                        "document_title": "document title",
                        "description": "document 1",
                        "section_number": "section number",
                        "section_title": "section title",
                    }
                ],
                "images": [
                    {
                        "original_file_name": "source_detail_image1.jpg",
                        "relative_url": "compliance/1/inspection/1/req_detail_images/source_detail_image1.jpg",
                    },
                    {
                        "original_file_name": "source_detail_image2.png",
                        "relative_url": "compliance/1/inspection/1/req_detail_images/source_detail_image2.png",
                    },
                ],
            }
        ],
    }

    default_value = {
        "summary": "requirement summary 4",
        "topic_id": 1,
        "req_type": InspectionRequirementTypeEnum.REQ.name,
        "enforcement_action_ids": [1, 7],
        "compliance_finding_id": 1,
        "findings": "requirement finding",
    }

    requirement_with_regulatory = {
        "summary": "Regulatory requirement summary",
        "topic_id": 2,
        "agency_id": 1,
        "req_type": InspectionRequirementTypeEnum.REG.name,
        "compliance_finding_id": 1,
        "findings": "Regulatory findings",
        "sort_order": 1,
    }

    requirement_with_images = {
        "summary": "Requirement with images",
        "topic_id": 3,
        "agency_id": None,
        "req_type": InspectionRequirementTypeEnum.REQ.name,
        "compliance_finding_id": None,
        "findings": "Findings with images",
        "photos": [
            {
                "original_file_name": "photo1.jpg",
                "date_taken": "2024-08-29T20:18:55.740Z",
                "taken_by_id": 1,
                "sort_order": 1,
                "caption": "caption 1",
                "relative_url": "compliance/1/inspection/1/requirement_images/filename1.jpg",
            }
        ],
        "figures": [
            {
                "original_file_name": "figure1.png",
                "date_taken": "2024-08-29T20:18:55.740Z",
                "taken_by_id": 1,
                "sort_order": 1,
                "caption": "caption 1",
                "relative_url": "compliance/1/inspection/1/requirement_images/filename1.jpg",
            }
        ],
    }

    requirement_with_enforcements = {
        "summary": "Requirement with enforcements",
        "topic_id": 4,
        "agency_id": None,
        "req_type": InspectionRequirementTypeEnum.REQ.name,
        "compliance_finding_id": None,
        "findings": "Findings with enforcements",
        "sort_order": 1,
        "enforcement_action_ids": [1, 2],
    }

    requirement_with_source_detail_images = {
        "summary": "Requirement with source detail images",
        "topic_id": 1,
        "req_type": InspectionRequirementTypeEnum.REQ.name,
        "compliance_finding_id": 1,
        "findings": "Requirement findings with source detail images",
        "requirement_source_details": [
            {
                "requirement_source_id": RequirementSourceEnum.ACT_2018.value,
                "section_number": "2.1",
                "title": "Source detail with images",
                "description": "Source detail description with images",
                "documents": [],
                "images": [
                    {
                        "original_file_name": "detail_evidence1.jpg",
                        "relative_url": "compliance/1/inspection/1/req_detail_images/detail_evidence1.jpg",
                    },
                    {
                        "original_file_name": "detail_evidence2.png",
                        "relative_url": "compliance/1/inspection/1/req_detail_images/detail_evidence2.png",
                    },
                    {
                        "original_file_name": "detail_evidence3.pdf",
                        "relative_url": "compliance/1/inspection/1/req_detail_images/detail_evidence3.pdf",
                    },
                ],
            },
            {
                "requirement_source_id": RequirementSourceEnum.REGULATION.value,
                "regulation_number": "123/2024",
                "title": "Second source detail",
                "description": "Second source detail with mixed content",
                "documents": [
                    {
                        "document_type_id": 1,
                        "document_title": "Regulation document",
                        "description": "Regulation compliance document",
                    }
                ],
                "images": [
                    {
                        "original_file_name": "regulation_image.jpg",
                        "relative_url": "compliance/1/inspection/1/req_detail_images/regulation_image.jpg",
                    }
                ],
            },
        ],
    }
