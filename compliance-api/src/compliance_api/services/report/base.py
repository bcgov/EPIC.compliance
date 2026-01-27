"""Report Generator Base Class."""
from abc import ABC, abstractmethod


class BaseReportGenerator(ABC):
    """Base class for report generators."""

    @abstractmethod
    def __init__(self, report_data):
        """Initialize the report generator with the provided report data."""
        self.report_data = report_data

    @abstractmethod
    def generate(self):
        """Generate the report."""
        pass
