import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE_PATH = BASE_DIR / "logs" / "compliance_app.log"

# Risk Weights for Different Sensitive Entity Types
# These weights are used by the risk classification engine to compute document risk.
RISK_WEIGHTS = {
    # High Risk Entities (Severe security or financial impact)
    "PASSWORD": 15,
    "API_KEY": 15,
    "CREDIT_CARD": 10,
    
    # Medium Risk Entities (Personally Identifiable Information & Finance)
    "PAN": 8,
    "AADHAAR": 8,
    "BANK_ACCOUNT": 8,
    "IFSC": 5,
    "EMPLOYEE_ID": 5,
    
    # Low Risk Entities (Basic contact details / general terms)
    "EMAIL": 2,
    "PHONE": 2,
    "CONFIDENTIAL_TERM": 3,
    "PERSON": 1,        # NER name detection
    "ORG": 1,           # NER organization
}

# Risk Rating Thresholds (Sum of all detected entity weights)
RISK_THRESHOLDS = {
    "LOW": 10,       # Total score < 10 is Low Risk
    "MEDIUM": 30,    # Total score between 10 and 30 is Medium Risk
    # Total score > 30 is High Risk
}

# spaCy Model Name
SPACY_MODEL = "en_core_web_sm"

# Custom Confidential business terms to scan for
CONFIDENTIAL_BUSINESS_TERMS = [
    "internal only",
    "confidential",
    "proprietary",
    "trade secret",
    "do not distribute",
    "restricted",
    "acquisition target",
    "patent pending",
    "non-disclosure agreement",
    "nda"
]
