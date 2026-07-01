import re
from typing import List
from src.detectors.base import BaseDetector, DetectedEntity
from src.utils.logger import setup_logger

logger = setup_logger("regex_detector")

class RegexDetector(BaseDetector):
    """
    Scans text line-by-line using regular expressions to detect structured 
    sensitive details like Aadhaar, PAN, Emails, Credit Cards, IFSC, and API Keys.
    """

    def __init__(self) -> None:
        # Predefined regex patterns for sensitive entities
        self.patterns = {
            "PAN": re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"),
            # Aadhaar: 12 digits, often spaced as 4-4-4
            "AADHAAR": re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b|\b\d{12}\b"),
            "EMAIL": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
            # Phone: Indian style or international phone numbers
            "PHONE": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?[789]\d{9}\b|\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"),
            # Credit Card: Standard 16 digit or spaced 4-4-4-4
            "CREDIT_CARD": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b|\b\d{13,19}\b"),
            # IFSC: 4 alphabetic characters, digit '0', then 6 alphanumeric characters
            "IFSC": re.compile(r"\b[A-Z]{4}0[A-Z0-9]{6}\b"),
            # Passwords (look for matching markers: password = abc, passwd: abc, pwd: abc)
            "PASSWORD": re.compile(
                r"\b(?:password|passwd|pwd|passcode)\s*[:=]\s*([a-zA-Z0-9@#$%^&*()_+=-]{6,20})\b",
                re.IGNORECASE
            ),
            # API Keys: Generic pattern checking for key declarations
            "API_KEY": re.compile(
                r"\b(?:api_key|apikey|client_secret|private_key|api[_-]?secret)\s*[:=]\s*[\"']?([a-zA-Z0-9_\-]{16,64})[\"']?\b",
                re.IGNORECASE
            ),
            # Employee ID: e.g., EMP-12345 or E12345
            "EMPLOYEE_ID": re.compile(
                r"\b(?:EMP|EMP_ID|EMPLOYEE_ID|STAFF_ID)\s*[:=]?\s*([a-zA-Z0-9\-]{4,10})\b",
                re.IGNORECASE
            )
        }

    def detect(self, text: str) -> List[DetectedEntity]:
        """
        Processes text line-by-line and records regex pattern matches.

        Args:
            text: Combined document text.

        Returns:
            List[DetectedEntity]: Discovered entities.
        """
        logger.info("Starting Regex scan on document text...")
        findings: List[DetectedEntity] = []
        
        if not text:
            return findings

        # Split text into lines to track location line-by-line
        lines = text.splitlines()
        
        for line_num, line in enumerate(lines, start=1):
            for entity_name, pattern in self.patterns.items():
                for match in pattern.finditer(line):
                    # For password/API Keys/Employee ID, we capture group 1 if it exists
                    # to extract only the value and not the 'password=' prompt itself.
                    if pattern.groups > 0 and match.lastindex is not None:
                        matched_val = match.group(match.lastindex).strip()
                    else:
                        matched_val = match.group(0).strip()
                    
                    # Clean surrounding quotes/colons
                    matched_val = matched_val.strip(":= \"'")
                    
                    # Skip empty matches
                    if not matched_val:
                        continue
                        
                    # Calculate dummy confidence (Regex matches have high structural confidence)
                    # For credit cards, we can do a simple Luhn check in the future if desired.
                    confidence = 0.95
                    
                    # Assign location metadata
                    location_desc = f"Line {line_num}"
                    
                    # Deduplicate: Avoid appending exact duplicate values for the same type at the same line
                    already_found = any(
                        f.entity_type == entity_name and f.matched_value == matched_val and f.location == location_desc
                        for f in findings
                    )
                    
                    if not already_found:
                        findings.append(
                            DetectedEntity(
                                entity_type=entity_name,
                                matched_value=matched_val,
                                confidence=confidence,
                                location=location_desc
                            )
                        )
                        
        logger.info(f"Regex scan complete. Detected {len(findings)} potential violations.")
        return findings
