import logging
import sys
from pathlib import Path
from typing import Optional

def setup_logger(
    name: str = "compliance_assistant",
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None
) -> logging.Logger:
    """
    Sets up and configures a standardized application-wide logger.
    
    Args:
        name: Name of the logger instance (usually namespaces the module).
        log_level: Logging severity threshold (e.g., logging.INFO, logging.DEBUG).
        log_file: Optional path to a file where logs should be appended.
        
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding duplicate handlers if the logger is already initialized
    if logger.handlers:
        return logger
        
    logger.setLevel(log_level)
    
    # Formatter specifying: Timestamp - Name of Module - Severity Level - Message
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Stream Handler (Stdout console logs)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler (Optional file persistence)
    if log_file:
        # Create directory structure for logs if it doesn't exist
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
    return logger
