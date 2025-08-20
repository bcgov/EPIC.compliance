"""EnforcementActionModel."""

from enum import Enum

from .option_base_model import OptionModel


class EnforcementActionOptionEnum(Enum):
    """EnforcementActionOptionEnum."""

    TO_BE_DETERMINED = 1
    NOT_APPLICABLE = 2
    NOTICE_OF_NON_COMPLIANCE = 3
    WARNING_LETTER = 4
    ORDER = 5
    ADMINISTRATIVE_PENALTY_RECOMMENDATION = 6
    REFERRAL_TO_ANOTHER_AGENCY = 7
    VIOLATION_TICKET = 8
    CHARGE_RECOMMENDATION = 9
    ADVISORY = 10
    WARNING = 11


class EnforcementActionOption(OptionModel):
    """Requirement source."""

    __tablename__ = "enforcement_action_options"
