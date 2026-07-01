from typing import List, Optional
from google import genai
from google.genai import types
from src.config import GEMINI_API_KEY
from src.detectors.base import DetectedEntity
from src.utils.logger import setup_logger

logger = setup_logger("gemini_service")

class GeminiService:
    """
    Integrates with Google Gemini API to analyze compliance risks, 
    generate professional summaries, and run natural language Q&A.
    """

    def __init__(self) -> None:
        self.api_key = GEMINI_API_KEY
        self.client = None
        
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            logger.error("Gemini API key is not configured. GenAI services will be unavailable.")
        else:
            try:
                # Initialize the new Google GenAI client
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Successfully initialized Gemini GenAI client.")
            except Exception as e:
                logger.critical(f"Failed to initialize Gemini GenAI client: {str(e)}")

    def is_available(self) -> bool:
        """
        Checks if the Gemini service is configured and ready.
        """
        return self.client is not None

    def generate_compliance_report(self, document_text: str, findings: List[DetectedEntity]) -> str:
        """
        Generates a professional compliance assessment using Gemini 2.5 Flash.

        Args:
            document_text: Raw text of the document.
            findings: List of sensitive data findings discovered by local scanners.

        Returns:
            str: Markdown-formatted compliance summary.
        """
        if not self.is_available():
            return (
                "❌ **Gemini API Key missing or invalid.**\n\n"
                "Please configure your `GEMINI_API_KEY` in the `.env` file to generate AI compliance summaries."
            )

        logger.info("Generating compliance report via Gemini...")
        
        # Format detected entities to send as structural context to Gemini
        findings_summary = ""
        if findings:
            findings_summary = "\n".join([
                f"- Found {f.entity_type} matched value '{f.matched_value}' at {f.location} (Confidence: {f.confidence:.2f})"
                for f in findings
            ])
        else:
            findings_summary = "No specific PII or security credentials detected by local scanners."

        # Truncate raw document text if it exceeds size (keep first 10,000 chars for safety)
        doc_snippet = document_text[:20000]
        if len(document_text) > 20000:
            doc_snippet += "\n...[TRUNCATED DUE TO SIZE]..."

        prompt = f"""
You are a Senior Compliance Officer and Cyber Security Specialist.
Analyze the following document context and the locally detected security findings.
Then, generate a detailed compliance and risk assessment report.

### Locally Detected Findings:
{findings_summary}

### Document Content Snippet:
{doc_snippet}

---

Please organize your response with the following markdown headers:
1. ## Executive Summary
   - Briefly summarize the document type, content, and security posture.
2. ## Compliance Observations
   - Assess regulatory alignments (e.g. GDPR, HIPAA, PCI-DSS, IT Act India).
   - Identify which clauses are potentially violated by the exposure of these details.
3. ## Security Risks
   - Explain the real-world threats of this data exposure (e.g., identity theft, financial fraud, credential stuffing).
4. ## Recommendations & Action Plan
   - Actionable advice for masking, encrypting, or deleting this data.
   - Access control configurations.
"""

        try:
            # Using the fast, cost-efficient gemini-2.5-flash model
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            logger.info("Gemini compliance report generated successfully.")
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API for compliance report: {str(e)}")
            return f"❌ **Error generating AI compliance report:** {str(e)}"

    def ask_question(self, document_text: str, question: str) -> str:
        """
        Allows users to ask natural language questions about the document.
        Uses the long-context capabilities of Gemini 2.5 Flash.

        Args:
            document_text: Complete text of the document.
            question: Natural language question query.

        Returns:
            str: Model's answer.
        """
        if not self.is_available():
            return "❌ **Gemini API Key missing or invalid.** QA functionality is disabled."

        logger.info(f"Asking Gemini: '{question}'...")

        # Inject context directly in prompt (Long Context Window approach)
        # Gemini 2.5 Flash easily handles up to 1M+ tokens.
        prompt = f"""
You are an expert compliance auditor. You are analyzing a document.
Using only the document text provided below, answer the user's question.
If the answer cannot be found in the text, politely state that it's not present in the document.

### Document Content:
{document_text}

---

### User Question:
{question}
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            logger.info("Gemini Q&A response received.")
            return response.text
        except Exception as e:
            logger.error(f"Error calling Gemini API for Q&A: {str(e)}")
            return f"❌ **Error retrieving response:** {str(e)}"
