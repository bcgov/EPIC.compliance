"""Complaint resolution model."""

from enum import Enum

from ..option_base_model import OptionModel


class ComplaintResolutionEnum(Enum):
    """ComplaintResolutionEnum."""

    INSPECTION_INVESTIGATION = 1
    REFERRED_TO_AGENCY = 2
    UNFOUNDED = 3


class ComplaintResolution(OptionModel):
    """ComplaintResolution."""

    __tablename__ = "complaint_resolutions"
