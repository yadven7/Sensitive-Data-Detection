from typing import List, Dict, Any
from src.detectors.base import DetectedEntity
from src.config import RISK_WEIGHTS, RISK_THRESHOLDS
from src.utils.logger import setup_logger

logger = setup_logger("risk_classifier")

class RiskClassifier:
    """
    Computes overall risk levels (Low, Medium, High) for analyzed documents 
    based on the frequency and severity of detected sensitive entities.
    """

    @staticmethod
    def classify(findings: List[DetectedEntity]) -> Dict[str, Any]:
        """
        Runs the scoring algorithm on the list of findings.

        Args:
            findings: List of detected entities.

        Returns:
            Dict: Structure containing risk_level, total_score, breakdowns, and justifications.
        """
        logger.info("Starting risk assessment classification...")
        total_score = 0
        entity_counts: Dict[str, int] = {}
        justifications: List[str] = []

        # 1. Calculate sum of weighted scores and count entities
        for finding in findings:
            entity_type = finding.entity_type
            weight = RISK_WEIGHTS.get(entity_type, 1)  # Default weight of 1 if unlisted
            
            total_score += weight
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

        # 2. Compile human-readable justifications
        for ent_type, count in entity_counts.items():
            weight_per_item = RISK_WEIGHTS.get(ent_type, 1)
            subtotal = count * weight_per_item
            justifications.append(
                f"Found {count} instance(s) of '{ent_type}' (Weight: {weight_per_item} pts each, Subtotal: {subtotal} pts)"
            )

        # 3. Determine overall risk level
        risk_level = "LOW"
        if total_score > RISK_THRESHOLDS["MEDIUM"]:
            risk_level = "HIGH"
        elif total_score >= RISK_THRESHOLDS["LOW"]:
            risk_level = "MEDIUM"

        logger.info(f"Risk assessment completed. Score: {total_score}, Level: {risk_level}")

        # Add generic guidance based on the risk level
        guidance = ""
        if risk_level == "HIGH":
            guidance = "CRITICAL: The document contains highly sensitive data (e.g., passwords, credentials, credit cards). Access should be immediately restricted, and the data should be masked or encrypted."
        elif risk_level == "MEDIUM":
            guidance = "WARNING: The document contains moderate PII or corporate identification numbers (e.g., PAN, Aadhaar, bank numbers). Share only via secure, authorized internal channels."
        else:
            guidance = "NOTICE: Low compliance risk. Only minor or general elements were identified (e.g., generic names or email addresses)."

        return {
            "risk_level": risk_level,
            "total_score": total_score,
            "entity_counts": entity_counts,
            "justifications": justifications,
            "guidance": guidance
        }
