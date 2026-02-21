"""
Base output plugin interface.
"""
from abc import ABC, abstractmethod
from typing import List, Dict
import logging


class BaseOutput(ABC):
    """Base class for all output plugins."""

    def __init__(self, output_config: dict, persona: dict):
        self.output_config = output_config
        self.persona = persona
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def save_tasks(self, tasks: List[Dict]) -> None:
        """Save extracted tasks to the output destination."""
        pass

    @abstractmethod
    def update_dashboard(self) -> None:
        """Update any dashboard or summary view."""
        pass
