"""test suit for agency."""

import json
from http import HTTPStatus
from urllib.parse import urljoin

from compliance_api.models.agency import Agency as AgencyModel
from tests.utilities.factory_scenario import AgencyScenario


API_BASE_URL = "/api/"


def test_get_agencies(app, client, auth_header_super_user):
    """Get agencies."""
    url = urljoin(API_BASE_URL, "agencies")
    #  create agencies
    AgencyScenario.create(AgencyScenario.agency1.value)
    AgencyScenario.create(AgencyScenario.agency2.value)
    result = client.get(url, headers=auth_header_super_user)
    assert len(result.json) == 8
    assert result.status_code == HTTPStatus.OK


def test_get_specific_agency(app, client, auth_header_super_user):
    """Get agency by id."""
    #  create agencies
    created_agency = AgencyScenario.create(AgencyScenario.agency1.value)
    # Store the ID before the session closes
    agency_id = created_agency.id
    agency_name = created_agency.name

    url = urljoin(API_BASE_URL, f"agencies/{agency_id}")
    result = client.get(url, headers=auth_header_super_user)
    print(result.json)
    assert result.status_code == HTTPStatus.OK
    assert result.json["id"] == agency_id
    assert result.json["name"] == agency_name


def test_create_agencies(client, auth_header_super_user):
    """Create agency."""
    url = urljoin(API_BASE_URL, "agencies")
    result = client.post(
        url,
        data=json.dumps(AgencyScenario.default_agency.value),
        headers=auth_header_super_user,
    )
    assert result.status_code == HTTPStatus.CREATED
    assert result.json["name"] == AgencyScenario.default_agency.value["name"]


def test_create_agencies_with_non_super_user(client, auth_header):
    """Create agency."""
    url = urljoin(API_BASE_URL, "agencies")
    result = client.post(
        url,
        data=json.dumps(AgencyScenario.default_agency.value),
        headers=auth_header,
    )
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_create_agencies_with_mandatory_missing(client, auth_header_super_user):
    """Create agency."""
    url = urljoin(API_BASE_URL, "agencies")
    create_dict = AgencyScenario.default_agency.value
    create_dict.pop("name")
    result = client.post(
        url, data=json.dumps(create_dict), headers=auth_header_super_user
    )
    response = json.loads(result.json["message"])
    assert "name" in response
    assert result.status_code == HTTPStatus.BAD_REQUEST


def test_update_agency(client, auth_header_super_user):
    """Update agency."""
    agency = AgencyScenario.create(AgencyScenario.agency1.value)
    url = urljoin(API_BASE_URL, f"agencies/{agency.id}")
    update_dict = AgencyScenario.agency1.value
    update_dict["name"] = "changed"
    result = client.patch(
        url, data=json.dumps(update_dict), headers=auth_header_super_user
    )
    assert result.json["name"] == update_dict["name"]
    assert result.status_code == HTTPStatus.OK


def test_update_agency_with_non_super_user(client, auth_header):
    """Update agency."""
    url = urljoin(API_BASE_URL, "agencies/1")
    update_dict = AgencyScenario.agency1.value
    result = client.patch(url, data=json.dumps(update_dict), headers=auth_header)
    assert result.status_code == HTTPStatus.FORBIDDEN


def test_delete_agency(client, auth_header_super_user):
    """Update agency."""
    agency = AgencyScenario.create(AgencyScenario.agency1.value)
    url = urljoin(API_BASE_URL, f"agencies/{agency.id}")
    result = client.delete(url, headers=auth_header_super_user)
    assert result.status_code == HTTPStatus.OK
    agency_get = AgencyModel.find_by_id(agency.id)
    print(agency.is_deleted)
    assert agency_get is None


def test_delete_agency_with_non_super_user(client, auth_header):
    """Update agency."""
    url = urljoin(API_BASE_URL, "agencies/1")
    result = client.delete(url, headers=auth_header)
    assert result.status_code == HTTPStatus.FORBIDDEN
