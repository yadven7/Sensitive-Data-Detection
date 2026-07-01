from typing import Dict, Type
from src.parsers.base import BaseParser
from src.parsers.pdf_parser import PDFParser
from src.parsers.csv_parser import CSVParser
from src.parsers.txt_parser import TXTParser
from src.utils.logger import setup_logger

logger = setup_logger("parser_factory")

class ParserFactory:
    """
    Factory class responsible for mapping file extensions 
    to their respective BaseParser implementations.
    """
    
    # Registry mapping file extensions to parser classes
    _registry: Dict[str, Type[BaseParser]] = {
        ".pdf": PDFParser,
        ".csv": CSVParser,
        ".txt": TXTParser
    }

    @classmethod
    def get_parser(cls, extension: str) -> BaseParser:
        """
        Retrieves a parser instance for a given file extension.

        Args:
            extension: File extension (including dot, e.g., '.pdf').

        Returns:
            BaseParser: An initialized parser instance.

        Raises:
            ValueError: If the file extension is unsupported.
        """
        ext_lower = extension.lower().strip()
        parser_cls = cls._registry.get(ext_lower)
        
        if not parser_cls:
            supported = ", ".join(cls._registry.keys())
            logger.error(f"Unsupported file extension requested: {ext_lower}")
            raise ValueError(
                f"Unsupported file type '{ext_lower}'. Supported formats are: {supported}"
            )
            
        logger.info(f"Instantiating parser for extension: {ext_lower}")
        return parser_cls()
