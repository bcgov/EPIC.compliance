"""Enum associated with Inspection model."""

import enum


class InspectionAttendanceOptionEnum(enum.Enum):
    """Attendance option enum."""

    AGENCIES = 1
    FIRSTNATIONS = 2
    MUNICIPAL = 3
    INDEPENDENT_ENVIRONMENTAL_MOINITOR = 4
    CERTIFICATE_HOLDER_OR_REGULATED_PARTY_REPRESENTATIVE = 5
    ATTENDING_OFFICERS = 8
    OTHER = 7


class InspectionStatusEnum(enum.Enum):
    """Inspection Status."""

    OPEN = "Open"
    CLOSED = "Closed"
    CANCELED = "Canceled"
    CLOSE_AS_NOTE = "Closed as Note to File"


class ImageTypeEnum(enum.Enum):
    """Type of images."""

    PHOTO = "Photo"
    FIGURE = "Figure"
