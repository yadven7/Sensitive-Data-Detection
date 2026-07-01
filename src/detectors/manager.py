from typing import List
from src.detectors.base import BaseDetector, DetectedEntity
from src.detectors.regex_detector import RegexDetector
from src.detectors.nlp_detector import NLPDetector
from src.utils.logger import setup_logger

logger = setup_logger("detection_manager")

class DetectionManager:
    """
    Orchestrates sensitive data scanners, aggregates findings, 
    and handles overlapping or duplicate entity detections.
    """

    def __init__(self) -> None:
        self.detectors: List[BaseDetector] = [
            RegexDetector(),
            NLPDetector()
        ]

    def scan(self, text: str) -> List[DetectedEntity]:
        """
        Executes all active detectors on the text and resolves conflicts.

        Args:
            text: Extracted document text.

        Returns:
            List[DetectedEntity]: Deduplicated and sorted list of violations.
        """
        logger.info("Initializing comprehensive document scan...")
        all_findings: List[DetectedEntity] = []

        for detector in self.detectors:
            try:
                findings = detector.detect(text)
                all_findings.extend(findings)
            except Exception as e:
                logger.error(f"Detector {detector.__class__.__name__} failed during execution: {str(e)}")

        # Deduplicate and resolve overlapping findings
        resolved_findings = self._resolve_conflicts(all_findings)
        
        # Sort findings by location line number numerically
        try:
            resolved_findings.sort(key=lambda x: int(x.location.split()[-1]) if x.location.split()[-1].isdigit() else 0)
        except Exception:
            pass  # Fallback if location string format differs
            
        logger.info(f"Scan finalized. Total unique entities identified: {len(resolved_findings)}")
        return resolved_findings

    def _resolve_conflicts(self, findings: List[DetectedEntity]) -> List[DetectedEntity]:
        """
        Resolves conflicts where different detectors match the same or overlapping text.
        For example:
        - If an email "test@corp.com" is detected as EMAIL (Regex) and ORG (spaCy),
          we retain the EMAIL match because it has higher specificity and confidence.
        """
        if not findings:
            return []

        resolved: List[DetectedEntity] = []
        
        # Sort by value length descending and confidence descending
        # This makes sure more specific, longer matches are analyzed first
        sorted_findings = sorted(findings, key=lambda x: (len(x.matched_value), x.confidence), reverse=True)
        
        for finding in sorted_findings:
            # Check if this exact text at this line is already covered by a better match
            overlap = False
            for existing in resolved:
                # Same location (line) check
                if existing.location == finding.location:
                    # Check if finding value is a substring of or exact match of existing value
                    if (finding.matched_value.lower() in existing.matched_value.lower() or 
                            existing.matched_value.lower() in finding.matched_value.lower()):
                        
                        # If existing type is generic (e.g. PERSON, ORG) and finding type is specific (e.g. PAN, EMAIL, AADHAAR),
                        # swap them. Otherwise, mark as overlap and discard finding.
                        generic_types = ["PERSON", "ORG"]
                        if existing.entity_type in generic_types and finding.entity_type not in generic_types:
                            # Replace existing generic with specific finding
                            resolved.remove(existing)
                            resolved.append(finding)
                        overlap = True
                        break
            
            if not overlap:
                resolved.append(finding)
                
        return resolved
