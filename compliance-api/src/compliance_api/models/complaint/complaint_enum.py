"""Enum associated with the complaint model."""

from enum import Enum


class ComplaintSourceEnum(Enum):
    """ComplaintSource Enum."""

    PUBLIC = 1
    FIRSTNATION = 2
    AGENCY = 3
    OTHER = 4
    FIRST_NATIONS_ALLIANCE = 5


class ComplaintRequirementSourceEnum(Enum):
    """ComplaintRequirementSourceEnum."""

    SCHEDULE_B = 1
    ORDER = 2
    EAC_CERTIFICATE = 3
    CERTIFIED_PROJECT_DESCRIPTION = 4
    ACT_2018 = 5
    COMPLIANCE_AGGREMENT = 6
    ACT_2002 = 7
    NOT_EA_ACT = 8
    OTHER = 9
