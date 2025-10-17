"""Test suite for inspection requirement."""

import copy
import json
from http import HTTPStatus
from urllib.parse import urljoin

from compliance_api.models import InspectionRequirement as InspectionRequirementModel
from compliance_api.models import InspectionStatusEnum, RequirementSourceEnum
from tests.utilities.factory_scenario.inspection_requirement_scenario import InspectionRequirementScenario


API_BASE_URL = "/api/inspections/"


def test_get_inspection_requirements(
    client, auth_header, created_inspection, created_inspection_requirement
):
    """Test getting all inspection requirements."""
    url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
    result = client.get(url, headers=auth_header)
    assert result.status_code == HTTPStatus.OK
    assert len(result.json) == 1
    assert isinstance(result.json, list)


def test_get_inspections_with_invalid_inspection_id(
    client, auth_header, created_inspection, created_inspection_requirement
):
    """Test getting all inspection requirements with invalid inspection ID."""
    url = urljoin(API_BASE_URL, "9999/requirements")
    result = client.get(url, headers=auth_header)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_get_inspection_requirement_by_id(
    client, auth_header_super_user, created_inspection, created_inspection_requirement
):
    """Test getting inspection requirement by ID."""
    url = urljoin(
        API_BASE_URL,
        f"{created_inspection.id}/requirements/{created_inspection_requirement.id}",
    )
    result = client.get(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == created_inspection_requirement.id


def test_create_inspection_requirement(
    client, auth_header_super_user, created_inspection
):
    """Test creating a new inspection requirement."""
    url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    result = client.post(
        url,
        data=json.dumps(requirement_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["inspection_id"] == created_inspection.id
    assert result.json["sort_order"] == 1


def test_create_inspection_requirement_with_images(
    client, auth_header_super_user, created_inspection, mock_doc_service
):
    """Test creating a requirement with photos and figures."""
    url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
    requirement_data = copy.copy(
        InspectionRequirementScenario.requirement_with_images.value
    )
    result = client.post(
        url,
        data=json.dumps(requirement_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED

    photo_url = urljoin(
        API_BASE_URL, f"{created_inspection.id}/requirements/{result.json['id']}/photos"
    )
    photo_result = client.get(photo_url, headers=auth_header_super_user)
    assert photo_result.status_code == HTTPStatus.OK
    assert len(photo_result.json) == 1

    figure_url = urljoin(
        API_BASE_URL,
        f"{created_inspection.id}/requirements/{result.json['id']}/figures",
    )
    figure_result = client.get(figure_url, headers=auth_header_super_user)
    assert figure_result.status_code == HTTPStatus.OK
    assert len(figure_result.json) == 1


def test_create_inspection_requirement_with_everything(
    client, auth_header_super_user, created_inspection
):
    """Test creating a requirement with everything including source detail images."""
    url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
    requirement_data = copy.copy(InspectionRequirementScenario.with_everything.value)
    result = client.post(
        url,
        data=json.dumps(requirement_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED

    # Verify requirement source details include images
    assert len(result.json["requirement_source_details"]) == 1
    source_detail = result.json["requirement_source_details"][0]
    assert "images" in source_detail
    assert len(source_detail["images"]) == 2
    assert (
        source_detail["images"][0]["original_file_name"] == "source_detail_image1.jpg"
    )
    assert (
        source_detail["images"][1]["original_file_name"] == "source_detail_image2.png"
    )


def test_create_inspection_requirement_with_all_requirement_sources(
    client, auth_header_super_user, created_inspection
):
    """Test creating requirements with all requirement sources."""
    url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")

    # Test each requirement source
    requirement_sources = [
        RequirementSourceEnum.SCHEDULE_B,
        # RequirementSourceEnum.ORDER,
        RequirementSourceEnum.EAC_CERTIFICATE,
        RequirementSourceEnum.CERTIFIED_PROJECT_DESCRIPTION,
        RequirementSourceEnum.ACT_2018,
        RequirementSourceEnum.COMPLIANCE_AGREEMENT,
        RequirementSourceEnum.ACT_2002,
        RequirementSourceEnum.OTHER,
        RequirementSourceEnum.EAC_AMENDMENT,
    ]

    for source in requirement_sources:
        requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
        requirement_source_detail = {
            "requirement_source_id": source.value,
            "title": f"Test requirement for {source.name}",
            "description": f"Description for {source.name} requirement",
            "documents": [],
        }

        # Add appropriate fields based on requirement source
        if source in [
            RequirementSourceEnum.ACT_2002,
            RequirementSourceEnum.ACT_2018,
            RequirementSourceEnum.COMPLIANCE_AGREEMENT,
            RequirementSourceEnum.CERTIFIED_PROJECT_DESCRIPTION,
            RequirementSourceEnum.OTHER,
        ]:
            requirement_source_detail["section_number"] = "1.1"

        if source in [
            RequirementSourceEnum.SCHEDULE_B,
            RequirementSourceEnum.EAC_CERTIFICATE,
            RequirementSourceEnum.EAC_AMENDMENT,
        ]:
            requirement_source_detail["condition_number"] = "1"

        if source == RequirementSourceEnum.EAC_AMENDMENT:
            requirement_source_detail["amendment_number"] = "A1"

        if source == RequirementSourceEnum.ORDER:
            requirement_source_detail["order_id"] = 1

        requirement_data["requirement_source_details"] = [requirement_source_detail]

        result = client.post(
            url,
            data=json.dumps(requirement_data),
            headers=auth_header_super_user,
        )
        assert result.status_code == HTTPStatus.CREATED
        assert (
            result.json["requirement_source_details"][0]["requirement_source_id"]
            == source.value
        )
        assert (
            result.json["requirement_source_details"][0]["title"]
            == f"Test requirement for {source.name}"
        )


def test_create_inspection_requirement_with_source_detail_images(
    client, auth_header_super_user, created_inspection
):
    """Test creating a requirement with source detail images."""
    url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
    requirement_data = copy.copy(
        InspectionRequirementScenario.requirement_with_source_detail_images.value
    )
    result = client.post(
        url,
        data=json.dumps(requirement_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert len(result.json["requirement_source_details"]) == 2

    # Check first source detail with images
    first_detail = result.json["requirement_source_details"][0]
    assert len(first_detail["images"]) == 3
    assert first_detail["images"][0]["original_file_name"] == "detail_evidence1.jpg"
    assert first_detail["images"][1]["original_file_name"] == "detail_evidence2.png"
    assert first_detail["images"][2]["original_file_name"] == "detail_evidence3.pdf"

    # Check second source detail with mixed content
    second_detail = result.json["requirement_source_details"][1]
    assert len(second_detail["documents"]) == 1
    assert len(second_detail["images"]) == 1
    assert second_detail["images"][0]["original_file_name"] == "regulation_image.jpg"


def test_update_inspection_requirement(
    client, auth_header_super_user, created_inspection, created_inspection_requirement
):
    """Test updating an existing inspection requirement."""
    update_data = copy.copy(InspectionRequirementScenario.default_value.value)
    update_data["summary"] = "Updated description"
    url = urljoin(
        API_BASE_URL,
        f"{created_inspection.id}/requirements/{created_inspection_requirement.id}",
    )
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    print(result.json)
    assert result.status_code == HTTPStatus.OK
    assert result.json["summary"] == "Updated description"


def test_update_inspection_requirement_with_source_detail_images(
    client, auth_header_super_user, created_inspection, created_inspection_requirement
):
    """Test updating an existing inspection requirement with source detail images."""
    update_data = copy.copy(
        InspectionRequirementScenario.requirement_with_source_detail_images.value
    )
    update_data["summary"] = "Updated requirement with source detail images"

    url = urljoin(
        API_BASE_URL,
        f"{created_inspection.id}/requirements/{created_inspection_requirement.id}",
    )
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.OK
    assert result.json["summary"] == "Updated requirement with source detail images"
    assert len(result.json["requirement_source_details"]) == 2

    # Verify images are included in response
    first_detail = result.json["requirement_source_details"][0]
    assert "images" in first_detail
    assert len(first_detail["images"]) == 3

    second_detail = result.json["requirement_source_details"][1]
    assert "images" in second_detail
    assert len(second_detail["images"]) == 1


def test_delete_inspection_requirement(
    client,
    auth_header_super_user,
    created_inspection,
    created_inspection_requirement,
):
    """Test deleting an inspection requirement."""
    url = urljoin(
        API_BASE_URL,
        f"{created_inspection.id}/requirements/{created_inspection_requirement.id}",
    )
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.NO_CONTENT
    # Verify deletion
    deleted_req = InspectionRequirementModel.find_by_id(
        created_inspection_requirement.id
    )
    assert deleted_req is None


def test_create_requirement_with_invalid_inspection(
    client,
    auth_header_super_user,
):
    """Test creating requirement with invalid inspection ID."""
    url = urljoin(API_BASE_URL, "9999/requirements")
    print(url)
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    result = client.post(
        url,
        data=json.dumps(requirement_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_create_requirement_with_closed_inspection(
    client,
    auth_header_super_user,
    created_inspection,
):
    """Test creating requirement for a closed inspection."""
    # Update inspection status to closed
    created_inspection.inspection_status = InspectionStatusEnum.CLOSED
    created_inspection.save()

    url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    result = client.post(
        url,
        data=json.dumps(requirement_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_update_requirement_with_invalid_id(
    client,
    auth_header_super_user,
    created_inspection,
):
    """Test updating non-existent requirement."""
    url = urljoin(API_BASE_URL, "9998/requirements/9998")
    requirement_data = copy.copy(InspectionRequirementScenario.with_everything.value)
    print(requirement_data)
    result = client.patch(
        url,
        data=json.dumps(requirement_data),
        headers=auth_header_super_user,
    )
    print(result.json)
    assert result.status_code == HTTPStatus.NOT_FOUND


def test_update_requirement_with_invalid_inspection_status(
    client,
    auth_header_super_user,
    created_inspection,
    created_inspection_requirement,
):
    """Test updating requirement when inspection is closed."""
    # Update inspection status to closed
    created_inspection.inspection_status = InspectionStatusEnum.CLOSED
    created_inspection.save()

    url = urljoin(
        API_BASE_URL,
        f"{created_inspection.id}/requirements/{created_inspection_requirement.id}",
    )
    update_data = {
        "description": "Updated description",
    }
    result = client.patch(
        url,
        data=json.dumps(update_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_sort_order_handling(
    client,
    auth_header_super_user,
    created_inspection,
):
    """Test sort order handling when creating multiple requirements."""
    url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")

    # Create first requirement
    requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
    result = client.post(
        url,
        data=json.dumps(requirement_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    first_req_id = result.json["id"]
    assert result.json["sort_order"] == 1

    # Create second requirement
    result = client.post(
        url,
        data=json.dumps(requirement_data),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["sort_order"] == 2

    # Verify first requirement's sort order is still 1
    first_req = InspectionRequirementModel.find_by_id(first_req_id)
    assert first_req.sort_order == 1


# def test_get_requirement_detail_images_success(
#     client, auth_header_super_user, created_inspection, mock_doc_service
# ):
#     """Test getting requirement detail images successfully."""
#     # Create a requirement with source detail images
#     url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
#     requirement_data = copy.copy(
#         InspectionRequirementScenario.requirement_with_source_detail_images.value
#     )
#     result = client.post(
#         url,
#         data=json.dumps(requirement_data),
#         headers=auth_header_super_user,
#     )
#     assert result.status_code == HTTPStatus.CREATED
#     requirement_id = result.json["id"]
#     detail_id = result.json["requirement_source_details"][0]["id"]

#     # Get images for the requirement detail
#     images_url = urljoin(
#         API_BASE_URL,
#         f"{created_inspection.id}/requirements/{requirement_id}/requirement-detail/{detail_id}/images",
#     )
#     images_result = client.get(images_url, headers=auth_header_super_user)
#     assert images_result.status_code == HTTPStatus.OK
#     assert isinstance(images_result.json, list)
#     assert len(images_result.json) == 3
#     # Verify presigned URL is included
#     assert "url" in images_result.json[0]
#     assert images_result.json[0]["url"] == "https://mocked-presigned-url.com"
#     assert images_result.json[0]["original_file_name"] == "detail_evidence1.jpg"


# def test_get_requirement_detail_images_with_invalid_inspection_id(
#     client, auth_header_super_user
# ):
#     """Test getting requirement detail images with invalid inspection ID."""
#     url = urljoin(
#         API_BASE_URL,
#         "9999/requirements/1/requirement-detail/1/images",
#     )
#     result = client.get(url, headers=auth_header_super_user)
#     assert result.status_code == HTTPStatus.NOT_FOUND


# def test_get_requirement_detail_images_with_invalid_requirement_id(
#     client, auth_header_super_user, created_inspection
# ):
#     """Test getting requirement detail images with invalid requirement ID."""
#     url = urljoin(
#         API_BASE_URL,
#         f"{created_inspection.id}/requirements/9999/requirement-detail/1/images",
#     )
#     result = client.get(url, headers=auth_header_super_user)
#     assert result.status_code == HTTPStatus.NOT_FOUND


# def test_get_requirement_detail_images_with_invalid_detail_id(
#     client, auth_header_super_user, created_inspection, created_inspection_requirement
# ):
#     """Test getting requirement detail images with invalid detail ID."""
#     url = urljoin(
#         API_BASE_URL,
#         f"{created_inspection.id}/requirements/{created_inspection_requirement.id}/requirement-detail/9999/images",
#     )
#     result = client.get(url, headers=auth_header_super_user)
#     assert result.status_code == HTTPStatus.NOT_FOUND


# def test_get_requirement_detail_images_with_mismatched_detail_id(
#     client, auth_header_super_user, created_inspection, mock_doc_service
# ):
#     """Test getting requirement detail images when detail doesn't belong to requirement."""
#     # Create first requirement with source detail
#     url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
#     requirement_data1 = copy.copy(
#         InspectionRequirementScenario.requirement_with_source_detail_images.value
#     )
#     result1 = client.post(
#         url,
#         data=json.dumps(requirement_data1),
#         headers=auth_header_super_user,
#     )
#     assert result1.status_code == HTTPStatus.CREATED
#     requirement1_id = result1.json["id"]
#     detail1_id = result1.json["requirement_source_details"][0]["id"]

#     # Create second requirement with source detail
#     requirement_data2 = copy.copy(
#         InspectionRequirementScenario.requirement_with_source_detail_images.value
#     )
#     result2 = client.post(
#         url,
#         data=json.dumps(requirement_data2),
#         headers=auth_header_super_user,
#     )
#     assert result2.status_code == HTTPStatus.CREATED
#     requirement2_id = result2.json["id"]

#     # Try to get detail1's images using requirement2's ID
#     images_url = urljoin(
#         API_BASE_URL,
#         f"{created_inspection.id}/requirements/{requirement2_id}/requirement-detail/{detail1_id}/images",
#     )
#     images_result = client.get(images_url, headers=auth_header_super_user)
#     assert images_result.status_code == HTTPStatus.NOT_FOUND


# def test_get_requirement_detail_images_empty_list(
#     client, auth_header_super_user, created_inspection, mock_doc_service
# ):
#     """Test getting requirement detail images when no images exist."""
#     # Create a requirement with source detail but no images
#     url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
#     requirement_data = copy.copy(InspectionRequirementScenario.default_value.value)
#     result = client.post(
#         url,
#         data=json.dumps(requirement_data),
#         headers=auth_header_super_user,
#     )
#     assert result.status_code == HTTPStatus.CREATED
#     requirement_id = result.json["id"]
#     detail_id = result.json["requirement_source_details"][0]["id"]

#     # Get images for the requirement detail
#     images_url = urljoin(
#         API_BASE_URL,
#         f"{created_inspection.id}/requirements/{requirement_id}/requirement-detail/{detail_id}/images",
#     )
#     images_result = client.get(images_url, headers=auth_header_super_user)
#     assert images_result.status_code == HTTPStatus.OK
#     assert isinstance(images_result.json, list)
#     assert len(images_result.json) == 0


# def test_get_requirement_detail_images_unauthorized(
#     client, created_inspection, mock_doc_service
# ):
#     """Test getting requirement detail images without authentication."""
#     url = urljoin(
#         API_BASE_URL,
#         f"{created_inspection.id}/requirements/1/requirement-detail/1/images",
#     )
#     result = client.get(url)
#     assert result.status_code == HTTPStatus.UNAUTHORIZED


# def test_get_requirement_detail_images_multiple_details(
#     client, auth_header_super_user, created_inspection, mock_doc_service
# ):
#     """Test getting images from different requirement details."""
#     # Create a requirement with multiple source details
#     url = urljoin(API_BASE_URL, f"{created_inspection.id}/requirements")
#     requirement_data = copy.copy(
#         InspectionRequirementScenario.requirement_with_source_detail_images.value
#     )
#     result = client.post(
#         url,
#         data=json.dumps(requirement_data),
#         headers=auth_header_super_user,
#     )
#     assert result.status_code == HTTPStatus.CREATED
#     requirement_id = result.json["id"]

#     # Get images for first detail
#     detail1_id = result.json["requirement_source_details"][0]["id"]
#     images_url1 = urljoin(
#         API_BASE_URL,
#         f"{created_inspection.id}/requirements/{requirement_id}/requirement-detail/{detail1_id}/images",
#     )
#     images_result1 = client.get(images_url1, headers=auth_header_super_user)
#     assert images_result1.status_code == HTTPStatus.OK
#     assert len(images_result1.json) == 3

#     # Get images for second detail
#     detail2_id = result.json["requirement_source_details"][1]["id"]
#     images_url2 = urljoin(
#         API_BASE_URL,
#         f"{created_inspection.id}/requirements/{requirement_id}/requirement-detail/{detail2_id}/images",
#     )
#     images_result2 = client.get(images_url2, headers=auth_header_super_user)
#     assert images_result2.status_code == HTTPStatus.OK
#     assert len(images_result2.json) == 1
#     assert images_result2.json[0]["original_file_name"] == "regulation_image.jpg"
