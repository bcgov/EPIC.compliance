"""Constants."""

from .enum import PermissionEnum


AUTH_APP = "COMPLIANCE"
INPUT_DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
UNAPPROVED_PROJECT_NAME = "Unapproved Project"
UNAPPROVED_PROJECT_CODE = "UNPRVD"
DELETE_DIC_PARAMS = {"is_active": False, "is_deleted": True}
OFFICE_NAME = "Environmental Assessment Office"
OFFICE_BRANCH = "Compliance and Enforcement Branch"
GROUP_MAP = {
    PermissionEnum.SUPERUSER: "super_user",
    PermissionEnum.VIEWER: "viewer",
    PermissionEnum.USER: "user",
    PermissionEnum.ADMIN: "admin",
}
