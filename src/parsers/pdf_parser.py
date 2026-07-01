import io
from src.parsers.base import BaseParser
from src.utils.logger import setup_logger

logger = setup_logger("pdf_parser")

class PDFParser(BaseParser):
    """
    Parser for PDF documents. Uses pdfplumber for robust structural layout and 
    table extraction, with a fallback to PyPDF2 for compatibility.
    """

    def parse(self, file_bytes: bytes) -> str:
        """
        Extracts all textual content from a PDF document.

        Args:
            file_bytes: Raw binary content of the PDF.

        Returns:
            str: Combined text extracted from all pages.
        """
        extracted_text = []
        file_like = io.BytesIO(file_bytes)

        # Method 1: Attempt extraction using pdfplumber (recommended for visual layouts)
        try:
            import pdfplumber
            logger.info("Attempting PDF text extraction using pdfplumber...")
            with pdfplumber.open(file_like) as pdf:
                for idx, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        extracted_text.append(page_text)
                    else:
                        logger.warning(f"No text found on PDF page {idx + 1} with pdfplumber.")
            
            combined = "\n\n".join(extracted_text)
            if combined.strip():
                logger.info("PDF text extraction via pdfplumber successful.")
                return combined
        except Exception as e:
            logger.error(f"pdfplumber extraction failed: {str(e)}. Falling back to PyPDF2...")

        # Method 2: Fallback to PyPDF2 if pdfplumber fails or returns empty text
        try:
            import PyPDF2
            file_like.seek(0)  # Reset stream position
            reader = PyPDF2.PdfReader(file_like)
            extracted_text = []
            
            for idx in range(len(reader.pages)):
                page = reader.pages[idx]
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
                    
            combined = "\n\n".join(extracted_text)
            if combined.strip():
                logger.info("PDF text extraction via PyPDF2 successful.")
                return combined
            else:
                raise ValueError("Both pdfplumber and PyPDF2 returned empty text.")
                
        except Exception as e:
            logger.critical(f"All PDF parsing methods failed: {str(e)}")
            raise RuntimeError(f"Failed to parse PDF document: {str(e)}")
