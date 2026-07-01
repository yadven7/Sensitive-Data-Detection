import spacy
from typing import List
from src.detectors.base import BaseDetector, DetectedEntity
from src.config import SPACY_MODEL, CONFIDENTIAL_BUSINESS_TERMS
from src.utils.logger import setup_logger

logger = setup_logger("nlp_detector")

class NLPDetector(BaseDetector):
    """
    NLP detector that scans text for names (PERSON) and organizations (ORG) 
    using spaCy, and searches for proprietary business terms.
    """

    def __init__(self) -> None:
        self.nlp = None
        try:
            # Attempt to load the pre-downloaded English model
            self.nlp = spacy.load(SPACY_MODEL)
            logger.info(f"Successfully loaded spaCy model: {SPACY_MODEL}")
        except Exception as e:
            logger.error(
                f"Failed to load spaCy model '{SPACY_MODEL}': {str(e)}. "
                "NLP Named Entity Recognition will be bypassed."
            )

    def detect(self, text: str) -> List[DetectedEntity]:
        """
        Scans text for Named Entities (via spaCy) and Confidential Terms.

        Args:
            text: Extracted document text.

        Returns:
            List[DetectedEntity]: List of detected names, orgs, and confidential terms.
        """
        findings: List[DetectedEntity] = []
        if not text:
            return findings

        # 1. Named Entity Recognition (NER) scanning
        if self.nlp:
            try:
                # Limit text processing length to avoid memory spikes in large documents
                max_length = 500000
                doc_text = text[:max_length]
                if len(text) > max_length:
                    logger.warning(f"Text truncated to {max_length} characters for spaCy parsing.")
                
                doc = self.nlp(doc_text)
                
                for ent in doc.ents:
                    # We are interested in names and organizations for privacy risk compliance
                    if ent.label_ in ["PERSON", "ORG"]:
                        # Exclude short fragments or formatting artifacts
                        clean_value = ent.text.strip()
                        if len(clean_value) < 2:
                            continue
                            
                        # Estimate line location based on characters
                        char_index = ent.start_char
                        line_num = text[:char_index].count("\n") + 1
                        
                        findings.append(
                            DetectedEntity(
                                entity_type=ent.label_,
                                matched_value=clean_value,
                                confidence=0.80 if ent.label_ == "PERSON" else 0.70,
                                location=f"Line {line_num}"
                            )
                        )
            except Exception as e:
                logger.error(f"Error during spaCy NER scanning: {str(e)}")

        # 2. Confidential Business Terms scan (substring matching)
        try:
            lines = text.splitlines()
            for line_num, line in enumerate(lines, start=1):
                line_lower = line.lower()
                for term in CONFIDENTIAL_BUSINESS_TERMS:
                    if term.lower() in line_lower:
                        # Find occurrences in the line to get exact string casing
                        start_idx = 0
                        while True:
                            idx = line_lower.find(term.lower(), start_idx)
                            if idx == -1:
                                break
                            
                            matched_val = line[idx : idx + len(term)].strip()
                            
                            # Check duplicates
                            already_found = any(
                                f.entity_type == "CONFIDENTIAL_TERM" and 
                                f.matched_value.lower() == matched_val.lower() and 
                                f.location == f"Line {line_num}"
                                for f in findings
                            )
                            
                            if not already_found:
                                findings.append(
                                    DetectedEntity(
                                        entity_type="CONFIDENTIAL_TERM",
                                        matched_value=matched_val,
                                        confidence=0.90,
                                        location=f"Line {line_num}"
                                    )
                                )
                            start_idx = idx + 1
        except Exception as e:
            logger.error(f"Error during confidential terms scan: {str(e)}")

        logger.info(f"NLP & Keyword scan complete. Found {len(findings)} matches.")
        return findings
