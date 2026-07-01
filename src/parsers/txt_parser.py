from src.parsers.base import BaseParser
from src.utils.logger import setup_logger

logger = setup_logger("txt_parser")

class TXTParser(BaseParser):
    """
    Parser for plain text files. Attempts to decode the raw bytes 
    using common encodings.
    """

    def parse(self, file_bytes: bytes) -> str:
        """
        Decodes raw bytes into a string.

        Args:
            file_bytes: Raw binary content of the text file.

        Returns:
            str: Decoded text contents.
        """
        encodings = ["utf-8", "latin1", "cp1252", "utf-16"]
        
        for encoding in encodings:
            try:
                decoded_text = file_bytes.decode(encoding)
                logger.info(f"Successfully decoded TXT file using {encoding}.")
                return decoded_text
            except UnicodeDecodeError:
                logger.warning(f"Failed to decode TXT using encoding: {encoding}")
                
        logger.critical("All decoders failed for TXT file.")
        raise ValueError("Could not decode TXT file. Ensure it is encoded in UTF-8 or standard Latin1.")
