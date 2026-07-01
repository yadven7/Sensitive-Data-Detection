from abc import ABC, abstractmethod

class BaseParser(ABC):
    """
    Abstract Base Class (ABC) defining the contract for all document parsers.
    Any format-specific parser (PDF, CSV, TXT) must inherit from this class 
    and implement the 'parse' method.
    """

    @abstractmethod
    def parse(self, file_bytes: bytes) -> str:
        """
        Parses raw file bytes and extracts text representation.

        Args:
            file_bytes: Raw binary data of the uploaded document.

        Returns:
            str: Extracted text content of the document.
            
        Raises:
            Exception: If there's an error reading or decoding the file.
        """
        pass
