"""
Base source plugin interface.
All source plugins must implement extract() and is_available().
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from datetime import datetime, timedelta
import logging


class BaseSource(ABC):
    """Base class for all source plugins."""

    def __init__(self, source_config: dict, persona: dict):
        self.source_config = source_config
        self.persona = persona
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def extract(self) -> List[Dict]:
        """
        Extract raw items from the source.
        Returns list of dicts with structure:
        {
            'content': str,          # The actual text content
            'author': str,           # Who wrote/said it
            'timestamp': datetime,   # When it was created
            'url': str,              # Link back to source
            'metadata': dict,        # Source-specific metadata
        }
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this source is available and accessible."""
        pass

    def is_within_lookback(self, timestamp: datetime, lookback_hours: int) -> bool:
        """Check if a timestamp is within the lookback period."""
        cutoff = datetime.now() - timedelta(hours=lookback_hours)
        return timestamp >= cutoff
