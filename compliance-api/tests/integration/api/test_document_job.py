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
"""Test suite for document jobs."""

import json
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from urllib.parse import urljoin

import pytest
from faker import Faker

from compliance_api.config import get_named_config
from compliance_api.models import db
from compliance_api.models.document_job import DocumentJob, DocumentJobStatusEnum
from compliance_api.models.inspection_record import InspectionRecord
from compliance_api.services.document_job import DocumentJobService
from tests.utilities.factory_scenario.staff_scenario import StaffScenario
from tests.utilities.factory_utils import factory_auth_header


API_BASE_URL = "/api/"
fake = Faker()


@pytest.fixture
def inspection_record(created_inspection):
    """Fixture to create an inspection record."""
    return InspectionRecord.create_inspection_record(
        {
            "inspection_id": created_inspection.id,
            "ir_status_id": 1,
        }
    )


def make_header_claims(staff_user, config):
    """Make JWT header claims for a staff user."""
    return {
        "iss": config.JWT_OIDC_TEST_ISSUER,
        "sub": "f7a4a1d3-73a8-4cbc-a40f-bb1145302065",
        "firstname": staff_user.first_name,
        "lastname": staff_user.last_name,
        "preferred_username": staff_user.auth_user_guid,
        "groups": ["/COMPLIANCE/VIEWER"],
        "realm_access": {"roles": []},
        "resource_access": {"epic-compliance": {"roles": ["viewer"]}},
    }


def test_get_most_recent_document_job_success(client,
                                              created_staff,
                                              jwt,
                                              inspection_record,
                                              mock_track_service,
                                              mock_auth_service
                                              ):
    """Test getting most recent document job for user and inspection."""
    staff_user = created_staff

    # Create document jobs
    older_job_data = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "download_name": "older_document.pdf",
        "relative_url": "documents/older_123.pdf",
        "started_at": datetime.now(timezone.utc) - timedelta(minutes=1),
        "completed_at": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    DocumentJobService.create(older_job_data)
    newer_job_data = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.IN_PROGRESS.value,
        "download_name": "newer_document.pdf",
        "relative_url": "documents/newer_123.pdf",
        "started_at": datetime.now(timezone.utc),
    }
    newer_job = DocumentJobService.create(newer_job_data)

    # Auth header
    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/recent")
    result = client.get(url, headers=auth_header)

    assert result.status_code == HTTPStatus.OK
    response_data = result.json

    # Should return the most recent job
    assert response_data["id"] == newer_job.id
    assert response_data["download_name"] == "newer_document.pdf"
    assert response_data["status"] == DocumentJobStatusEnum.IN_PROGRESS.value


def test_user_can_only_see_their_own_document_jobs(client,
                                                   created_staff,
                                                   jwt,
                                                   inspection_record,
                                                   mock_track_service,
                                                   mock_auth_service
                                                   ):
    """Test user can only see their own document jobs."""
    staff_user = created_staff
    user_data = StaffScenario.default_data.value
    auth_user_guid = f"{fake.word()}{datetime.now().timestamp()}"
    user_data["auth_user_guid"] = auth_user_guid
    other_staff = StaffScenario.create(user_data)
    print(staff_user.id, other_staff.id)
    assert other_staff.id != staff_user.id

    # Create document jobs
    document_job_for_staff_user = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "download_name": "staff_user_document.pdf",
        "relative_url": "documents/older_123.pdf",
        "started_at": datetime.now(timezone.utc) - timedelta(hours=1),
        "completed_at": datetime.now(timezone.utc) - timedelta(hours=1),
    }
    staff_job = DocumentJobService.create(document_job_for_staff_user)
    document_job_for_other_staff = {
        "user_id": other_staff.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.IN_PROGRESS.value,
        "download_name": "other_user_document.pdf",
        "relative_url": "documents/newer_123.pdf",
        "started_at": datetime.now(timezone.utc),
    }
    DocumentJobService.create(document_job_for_other_staff)

    # Auth header
    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/recent")
    result = client.get(url, headers=auth_header)

    assert result.status_code == HTTPStatus.OK
    response_data = result.json

    # Should return the most recent job
    assert response_data["id"] == staff_job.id
    assert response_data["download_name"] == "staff_user_document.pdf"
    assert response_data["status"] == DocumentJobStatusEnum.COMPLETED.value


def test_user_can_delete_own_document_job(client,
                                          created_staff,
                                          jwt,
                                          inspection_record,
                                          mock_track_service,
                                          mock_auth_service
                                          ):
    """Test user can delete their own document job."""
    staff_user = created_staff

    # Create a document job for the staff user
    job_data = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "download_name": "delete_me.pdf",
        "relative_url": "documents/delete_me.pdf",
        "started_at": datetime.now(timezone.utc),
        "completed_at": datetime.now(timezone.utc),
    }
    job = DocumentJobService.create(job_data)

    # Auth header
    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/{job.id}")
    result = client.delete(url, headers=auth_header)

    assert result.status_code == HTTPStatus.NO_CONTENT

    # Optionally, verify the job is actually deleted (if service supports it)
    deleted_job = DocumentJob.find_by_id(job.id)
    assert deleted_job is None


def test_user_cannot_delete_other_users_document_job(client,
                                                     created_staff,
                                                     jwt,
                                                     inspection_record,
                                                     mock_track_service,
                                                     mock_auth_service
                                                     ):
    """Test user cannot delete another user's document job."""
    staff_user = created_staff
    user_data = StaffScenario.default_data.value
    auth_user_guid = f"{fake.word()}{datetime.now().timestamp()}"
    user_data["auth_user_guid"] = auth_user_guid
    other_staff = StaffScenario.create(user_data)
    assert other_staff.id != staff_user.id

    # Create a document job for the other staff user
    job_data = {
        "user_id": other_staff.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "download_name": "other_user_delete_me.pdf",
        "relative_url": "documents/other_user_delete_me.pdf",
        "started_at": datetime.now(timezone.utc),
        "completed_at": datetime.now(timezone.utc),
    }
    job = DocumentJobService.create(job_data)

    # Auth header for staff_user (not the owner)
    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/{job.id}")
    result = client.delete(url, headers=auth_header)

    assert result.status_code in (HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND)

    # Ensure the job still exists
    still_exists = DocumentJob.find_by_id(job.id)
    assert still_exists is not None


def test_put_update_document_job_success(client,
                                         created_staff,
                                         jwt,
                                         inspection_record,
                                         mock_track_service,
                                         mock_auth_service
                                         ):
    """Test updating a document job with valid data."""
    staff_user = created_staff
    job_data = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.IN_PROGRESS.value,
        "download_name": "to_update.pdf",
        "relative_url": "documents/to_update.pdf",
        "started_at": datetime.now(timezone.utc),
    }
    job = DocumentJobService.create(job_data)

    update_data = {
        "status": DocumentJobStatusEnum.FAILED.value,
    }
    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/{job.id}")
    result = client.put(url, headers=auth_header, data=json.dumps(update_data), content_type='application/json')

    assert result.status_code == HTTPStatus.OK
    response_data = result.json
    assert response_data["id"] == job.id
    assert response_data["status"] == DocumentJobStatusEnum.FAILED.value


def test_put_update_document_job_returns_404_for_nonexistent(client,
                                                             created_staff,
                                                             jwt,
                                                             mock_track_service,
                                                             mock_auth_service
                                                             ):
    """Test updating a non-existent document job returns 404."""
    staff_user = created_staff
    non_existent_job_id = 9999999

    update_data = {
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "download_name": "does_not_exist.pdf"
    }
    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/{non_existent_job_id}")
    result = client.put(url, headers=auth_header, data=json.dumps(update_data), content_type='application/json')

    assert result.status_code == HTTPStatus.NOT_FOUND
    assert "not found" in result.json.get("message", "").lower()


def test_user_cannot_update_other_users_document_job(client,
                                                     created_staff,
                                                     jwt,
                                                     inspection_record,
                                                     mock_track_service,
                                                     mock_auth_service
                                                     ):
    """Test a user cannot update someone else's document job."""
    staff_user = created_staff
    # Create a different staff user
    user_data = StaffScenario.default_data.value
    auth_user_guid = f"{fake.word()}{datetime.now().timestamp()}"
    user_data["auth_user_guid"] = auth_user_guid
    other_staff = StaffScenario.create(user_data)
    assert staff_user.id != other_staff.id

    job_data = {
        "user_id": other_staff.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.IN_PROGRESS.value,
        "download_name": "other_user_update.pdf",
        "relative_url": "documents/other_user_update.pdf",
        "started_at": datetime.now(timezone.utc),
    }
    job = DocumentJobService.create(job_data)

    update_data = {
        "status": DocumentJobStatusEnum.FAILED.value,
        "download_name": "not_allowed.pdf"
    }

    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/{job.id}")
    result = client.put(url, headers=auth_header, data=json.dumps(update_data), content_type='application/json')

    assert result.status_code == HTTPStatus.NOT_FOUND


def test_delete_document_job_requires_auth(client,
                                           created_staff,
                                           inspection_record,
                                           mock_track_service,
                                           mock_auth_service
                                           ):
    """Test that deleting a job without auth header returns 401."""
    staff_user = created_staff
    job_data = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "download_name": "should_not_be_deleted.pdf",
        "relative_url": "documents/should_not_be_deleted.pdf",
        "started_at": datetime.now(timezone.utc),
        "completed_at": datetime.now(timezone.utc),
    }
    job = DocumentJobService.create(job_data)

    url = urljoin(API_BASE_URL, f"document-jobs/{job.id}")
    result = client.delete(url)

    assert result.status_code in (HTTPStatus.UNAUTHORIZED, 401)
    found = DocumentJob.find_by_id(job.id)
    assert found is not None


def test_put_document_job_requires_auth(client,
                                        created_staff,
                                        inspection_record,
                                        mock_track_service,
                                        mock_auth_service
                                        ):
    """Test updating a job without auth header returns 401."""
    staff_user = created_staff
    job_data = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "download_name": "update_no_auth.pdf",
        "relative_url": "documents/update_no_auth.pdf",
        "started_at": datetime.now(timezone.utc),
        "completed_at": datetime.now(timezone.utc),
    }
    job = DocumentJobService.create(job_data)

    update_data = {
        "status": DocumentJobStatusEnum.FAILED.value,
        "download_name": "now_failed.pdf"
    }

    url = urljoin(API_BASE_URL, f"document-jobs/{job.id}")
    result = client.put(url, data=json.dumps(update_data), content_type='application/json')

    assert result.status_code in (HTTPStatus.UNAUTHORIZED, 401)


def test_get_document_job_requires_auth(client, inspection_record):
    """Test fetching a document job requires auth."""
    url = urljoin(API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/recent")
    result = client.get(url)
    assert result.status_code in (HTTPStatus.UNAUTHORIZED, 401)


def test_last_generated_success(client, created_staff, jwt, inspection_record, mock_track_service, mock_auth_service):
    """Test getting last-generated time for user and inspection."""
    staff_user = created_staff
    # Create a document job for the staff user
    now = datetime.now(timezone.utc)
    job_data = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "download_name": "last_generated.pdf",
        "relative_url": "documents/last_generated.pdf",
        "started_at": now,
        "completed_at": now,
    }
    DocumentJobService.create(job_data)

    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/last-generated")
    result = client.get(url, headers=auth_header)

    assert result.status_code == HTTPStatus.OK
    response_data = result.json
    assert "last_generated_time" in response_data
    assert response_data["last_generated_time"] == now.isoformat()


def test_last_generated_requires_auth(client, inspection_record):
    """Test last-generated endpoint requires auth."""
    url = urljoin(API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/last-generated")
    result = client.get(url)
    assert result.status_code in (HTTPStatus.UNAUTHORIZED, 401)


def test_last_generated_no_jobs_returns_null(
    client,
    created_staff,
    jwt,
    inspection_record,
    mock_track_service,
    mock_auth_service
):
    """Test last-generated returns null if no jobs exist for user/inspection."""
    staff_user = created_staff
    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/last-generated")
    result = client.get(url, headers=auth_header)

    assert result.status_code == HTTPStatus.OK
    response_data = result.json
    assert "last_generated_time" in response_data
    assert response_data["last_generated_time"] is None


def test_recent_document_job_scoped_by_output_format(client,
                                                     created_staff,
                                                     jwt,
                                                     inspection_record,
                                                     mock_track_service,
                                                     mock_auth_service
                                                     ):
    """A pdf job and a docx job for the same user/IR should not collide."""
    staff_user = created_staff

    pdf_job_data = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "output_format": "pdf",
        "download_name": "report.pdf",
        "relative_url": "documents/report.pdf",
        "started_at": datetime.now(timezone.utc) - timedelta(minutes=5),
        "completed_at": datetime.now(timezone.utc) - timedelta(minutes=5),
    }
    pdf_job = DocumentJobService.create(pdf_job_data)

    docx_job_data = {
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.IN_PROGRESS.value,
        "output_format": "docx",
        "started_at": datetime.now(timezone.utc),
    }
    docx_job = DocumentJobService.create(docx_job_data)

    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    docx_url = urljoin(
        API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/recent?output_format=docx"
    )
    docx_result = client.get(docx_url, headers=auth_header)
    assert docx_result.status_code == HTTPStatus.OK
    assert docx_result.json["id"] == docx_job.id
    assert docx_result.json["status"] == DocumentJobStatusEnum.IN_PROGRESS.value

    pdf_url = urljoin(
        API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/recent?output_format=pdf"
    )
    pdf_result = client.get(pdf_url, headers=auth_header)
    assert pdf_result.status_code == HTTPStatus.OK
    assert pdf_result.json["id"] == pdf_job.id
    assert pdf_result.json["status"] == DocumentJobStatusEnum.COMPLETED.value


def test_last_generated_scoped_by_output_format(client,
                                                created_staff,
                                                jwt,
                                                inspection_record,
                                                mock_track_service,
                                                mock_auth_service
                                                ):
    """last-generated should only consider jobs matching the requested output_format."""
    staff_user = created_staff
    pdf_completed_at = datetime.now(timezone.utc) - timedelta(minutes=10)
    docx_completed_at = datetime.now(timezone.utc)

    DocumentJobService.create({
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "output_format": "pdf",
        "download_name": "report.pdf",
        "relative_url": "documents/report.pdf",
        "started_at": pdf_completed_at,
        "completed_at": pdf_completed_at,
    })
    DocumentJobService.create({
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "output_format": "docx",
        "download_name": "report.docx",
        "relative_url": "documents/report.docx",
        "started_at": docx_completed_at,
        "completed_at": docx_completed_at,
    })

    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    docx_url = urljoin(
        API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/last-generated?output_format=docx"
    )
    docx_result = client.get(docx_url, headers=auth_header)
    assert docx_result.status_code == HTTPStatus.OK
    assert docx_result.json["last_generated_time"] == docx_completed_at.isoformat()

    pdf_url = urljoin(
        API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/last-generated?output_format=pdf"
    )
    pdf_result = client.get(pdf_url, headers=auth_header)
    assert pdf_result.status_code == HTTPStatus.OK
    assert pdf_result.json["last_generated_time"] == pdf_completed_at.isoformat()


@pytest.fixture
def final_inspection_record(created_inspection):
    """Fixture to create a FINAL inspection record."""
    return InspectionRecord.create_inspection_record(
        {
            "inspection_id": created_inspection.id,
            "ir_status_id": 2,
        }
    )


def test_handle_background_job_docx_success(app, mocker, created_staff, inspection_record):
    """DOCX jobs should upload the rendered BytesIO stream and complete with a .docx name."""
    from io import BytesIO

    staff_user = created_staff
    job = DocumentJobService.create({
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.IN_PROGRESS.value,
        "output_format": "docx",
        "started_at": datetime.now(timezone.utc),
    })

    mock_inspection = mocker.MagicMock(ir_number="IR-0001")
    mocker.patch(
        "compliance_api.services.document_job.InspectionRecordService.render",
        return_value=(BytesIO(b"docx bytes"), mock_inspection),
    )
    mocker.patch(
        "compliance_api.services.document_job.DocService.get_presigned_url",
        return_value={
            "presigned_url": "https://example.com/presigned-url",
            "relative_url": "inspection_records/mock-uuid.docx",
        },
    )
    mock_put = mocker.patch("requests.put")
    mock_put.return_value.status_code = 200

    DocumentJobService.handle_background_job(
        app, job.id, "test-token", {}, inspection_record.inspection_id,
        inspection_record.id, staff_user.id, "docx",
    )

    # handle_background_job runs its updates in a separate app-context session
    # (mirroring the real background thread); expire the outer session's
    # identity-mapped copy so the committed changes are visible here.
    db.session.expire_all()
    updated_job = DocumentJob.find_by_id(job.id)
    assert updated_job.status == DocumentJobStatusEnum.COMPLETED.value
    #  The fixture record is PRELIMINARY, so the name carries the suffix
    assert updated_job.download_name == "IR-0001_PRELIMINARY.docx"
    assert updated_job.relative_url.endswith(".docx")
    mock_put.assert_called_once()
    assert mock_put.call_args.kwargs["data"].read() == b"docx bytes"


def test_handle_background_job_final_docx_has_no_preliminary_suffix(
    app, mocker, created_staff, final_inspection_record
):
    """FINAL DOCX records should keep the plain IR number as the download name."""
    from io import BytesIO

    staff_user = created_staff
    job = DocumentJobService.create({
        "user_id": staff_user.id,
        "inspection_record_id": final_inspection_record.id,
        "status": DocumentJobStatusEnum.IN_PROGRESS.value,
        "output_format": "docx",
        "started_at": datetime.now(timezone.utc),
    })

    mock_inspection = mocker.MagicMock(ir_number="IR-0001")
    mocker.patch(
        "compliance_api.services.document_job.InspectionRecordService.render",
        return_value=(BytesIO(b"docx bytes"), mock_inspection),
    )
    mocker.patch(
        "compliance_api.services.document_job.DocService.get_presigned_url",
        return_value={
            "presigned_url": "https://example.com/presigned-url",
            "relative_url": "inspection_records/mock-uuid.docx",
        },
    )
    mock_put = mocker.patch("requests.put")
    mock_put.return_value.status_code = 200

    DocumentJobService.handle_background_job(
        app, job.id, "test-token", {}, final_inspection_record.inspection_id,
        final_inspection_record.id, staff_user.id, "docx",
    )

    db.session.expire_all()
    updated_job = DocumentJob.find_by_id(job.id)
    assert updated_job.download_name == "IR-0001.docx"


def test_handle_background_job_preliminary_pdf_has_no_preliminary_suffix(
    app, mocker, created_staff, inspection_record
):
    """The suffix is a DOCX naming convention, so PDF names are left alone."""
    staff_user = created_staff
    job = DocumentJobService.create({
        "user_id": staff_user.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.IN_PROGRESS.value,
        "output_format": "pdf",
        "started_at": datetime.now(timezone.utc),
    })

    mock_inspection = mocker.MagicMock(ir_number="IR-0001")
    mock_response = mocker.MagicMock(content=b"pdf bytes")
    mocker.patch(
        "compliance_api.services.document_job.InspectionRecordService.render",
        return_value=(mock_response, mock_inspection),
    )
    mocker.patch(
        "compliance_api.services.document_job.DocService.get_presigned_url",
        return_value={
            "presigned_url": "https://example.com/presigned-url",
            "relative_url": "inspection_records/mock-uuid.pdf",
        },
    )
    mock_put = mocker.patch("requests.put")
    mock_put.return_value.status_code = 200

    DocumentJobService.handle_background_job(
        app, job.id, "test-token", {}, inspection_record.inspection_id,
        inspection_record.id, staff_user.id, "pdf",
    )

    db.session.expire_all()
    updated_job = DocumentJob.find_by_id(job.id)
    assert updated_job.download_name == "IR-0001.pdf"


def test_last_generated_other_user_job_returns_null(
    client,
    created_staff,
    jwt,
    inspection_record,
    mock_track_service,
    mock_auth_service
):
    """Test last-generated returns null if only a different user has a job for the inspection."""
    staff_user = created_staff
    # Create a different staff user
    user_data = StaffScenario.default_data.value
    auth_user_guid = f"other_{datetime.now().timestamp()}"
    user_data["auth_user_guid"] = auth_user_guid
    other_staff = StaffScenario.create(user_data)
    assert other_staff.id != staff_user.id

    # Create a document job for the other staff user
    job_data = {
        "user_id": other_staff.id,
        "inspection_record_id": inspection_record.id,
        "status": DocumentJobStatusEnum.COMPLETED.value,
        "download_name": "other_user_last_generated.pdf",
        "relative_url": "documents/other_user_last_generated.pdf",
        "started_at": datetime.now(timezone.utc),
        "completed_at": datetime.now(timezone.utc),
    }
    DocumentJobService.create(job_data)

    config = get_named_config("testing")
    header_claims = make_header_claims(staff_user, config)
    auth_header = factory_auth_header(jwt=jwt, claims=header_claims)

    url = urljoin(API_BASE_URL, f"document-jobs/inspections/{inspection_record.id}/last-generated")
    result = client.get(url, headers=auth_header)

    assert result.status_code == HTTPStatus.OK
    response_data = result.json
    assert "last_generated_time" in response_data
    assert response_data["last_generated_time"] is None
