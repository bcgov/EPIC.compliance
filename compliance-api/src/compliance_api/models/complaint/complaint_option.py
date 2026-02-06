"""Complaint Options."""

from enum import Enum
from ..option_base_model import OptionModel


class ComplaintSourceEnum(Enum):
    """Enumeration for Complaint Sources."""

    PUBLIC = "Public"
    FIRST_NATION = "First Nation"
    FIRST_NATIONS_ALLIANCE = "First Nations Alliance"
    AGENCY = "Agency"
    OTHER = "Other"


class ComplaintSource(OptionModel):
    """ComplaintSource model."""

    __tablename__ = "complaint_sources"
