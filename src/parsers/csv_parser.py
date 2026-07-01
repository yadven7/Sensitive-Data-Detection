import io
import pandas as pd
from src.parsers.base import BaseParser
from src.utils.logger import setup_logger

logger = setup_logger("csv_parser")

class CSVParser(BaseParser):
    """
    Parser for CSV documents. Reads data using Pandas and converts 
    it into a structured textual layout suitable for sensitive data analysis.
    """

    def parse(self, file_bytes: bytes) -> str:
        """
        Parses CSV raw bytes into a tabular text string.

        Args:
            file_bytes: Raw binary content of the CSV.

        Returns:
            str: String containing data representation.
        """
        file_like = io.BytesIO(file_bytes)
        
        # Try common encodings: utf-8, then latin1
        encodings = ["utf-8", "latin1", "cp1252"]
        df = None
        
        for encoding in encodings:
            try:
                file_like.seek(0)
                df = pd.read_csv(file_like, encoding=encoding)
                logger.info(f"Successfully read CSV using encoding: {encoding}")
                break
            except Exception as e:
                logger.warning(f"Failed to read CSV with encoding {encoding}: {str(e)}")
                
        if df is None:
            logger.critical("All attempts to read CSV failed due to encoding errors.")
            raise ValueError("Unsupported CSV encoding. Please use a UTF-8 encoded file.")
            
        # Check if dataframe is empty
        if df.empty:
            logger.warning("Uploaded CSV is empty.")
            return ""

        # Represent the CSV in a textual format.
        # Option A: raw to_string representation (great for regex match)
        # Option B: line-by-line format to preserve context (Column: Value)
        # Let's provide a structured layout where each row is represented.
        # This keeps the context visual so we can track line number/row index.
        lines = []
        
        # Add column header info
        headers = ", ".join(df.columns.astype(str))
        lines.append(f"Headers: {headers}\n")
        
        for idx, row in df.iterrows():
            row_items = []
            for col in df.columns:
                val = str(row[col]).strip()
                # Skip representation of standard pandas NaNs
                if val in ["nan", "NaN", "None", ""]:
                    continue
                row_items.append(f"{col}: {val}")
            
            row_str = f"Row {idx + 1}: " + " | ".join(row_items)
            lines.append(row_str)
            
        return "\n".join(lines)
