from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class DetectedEntity:
    """
    Data container representing a single discovered sensitive entity.
    """
    entity_type: str      # e.g., 'PAN', 'AADHAAR', 'PASSWORD', 'EMAIL'
    matched_value: str    # The actual matched text (e.g., 'ABCDE1234F')
    confidence: float     # Match confidence score (0.0 to 1.0)
    location: str         # Human-readable index or line (e.g., 'Line 12', 'Row 5', 'Character 40-52')

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the entity details into a serializable dictionary format.
        """
        return {
            "entity_type": self.entity_type,
            "matched_value": self.matched_value,
            "confidence": self.confidence,
            "location": self.location
        }

class BaseDetector(ABC):
    """
    Abstract interface that all custom scanners (Regex, NLP, Custom Keywords) 
    must implement.
    """

    @abstractmethod
    def detect(self, text: str) -> List[DetectedEntity]:
        """
        Scans text for sensitive information.

        Args:
            text: Raw extracted document text.

        Returns:
            List[DetectedEntity]: List of detected sensitive records.
        """
        pass
