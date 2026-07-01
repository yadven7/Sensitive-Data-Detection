import os
import csv
import subprocess
import sys
from pathlib import Path

# Ensure reportlab is installed for PDF generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    print("Installing reportlab for PDF generation support...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

# Set output test directory
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "test_samples"
OUTPUT_DIR.mkdir(exist_ok=True)

# Fake Sensitive Data to write
FAKE_PII_TEXT = """
CONFIDENTIAL BUSINESS REPORT - INTERNAL USE ONLY
This document contains proprietary trade secrets and non-disclosure agreement (NDA) details.

1. Employee Credentials:
- Administrator Password: password = AdminPass@2026!
- Service Account API Key: client_secret: sec_key_live_9876543210abcdef
- Employee ID: EMP-10492

2. Personal Information:
- Project Manager: Ramesh Kumar (Email: ramesh.kumar@dummycorp.com, Phone: +91 9876543210)
- Senior Consultant: Sarah Connor (Email: sarah.c@dummycorp.com, Phone: 555-019-2834)

3. Financial Records & Identification:
- PAN Card Number: ABCDE1234F
- Aadhaar Card Number: 1234 5678 9012
- Corporate Bank Account: IFSC Code: SBIN0001234 (State Bank of India), Account Number: 987654321098
- Business Credit Card: 4111-2222-3333-4444 (Exp: 12/28)
"""

def generate_txt():
    """Generates a text file with mock sensitive data."""
    file_path = OUTPUT_DIR / "sample_pii.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(FAKE_PII_TEXT)
    print(f"Generated TXT sample: {file_path}")

def generate_csv():
    """Generates a CSV file with columns holding mock sensitive values."""
    file_path = OUTPUT_DIR / "sample_pii.csv"
    data = [
        ["EmployeeID", "Name", "Email", "Phone", "PAN", "Aadhaar", "CreditCard"],
        ["EMP-1001", "Aarav Sharma", "aarav.s@dummycorp.com", "9876543210", "AAAAA1111A", "1111 2222 3333", "4111222233334444"],
        ["EMP-1002", "Diya Patel", "diya.p@dummycorp.com", "8765432109", "BBBBB2222B", "2222 3333 4444", "5111222233334444"],
        ["EMP-1003", "John Doe", "john.doe@dummycorp.com", "555-019-1234", "", "", "378282246310005"]
    ]
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(data)
    print(f"Generated CSV sample: {file_path}")

def generate_pdf():
    """Generates a PDF file with mock sensitive data using ReportLab."""
    file_path = OUTPUT_DIR / "sample_pii.pdf"
    
    # Initialize reportlab canvas
    c = canvas.Canvas(str(file_path), pagesize=letter)
    width, height = letter
    
    # Write Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "GUARDIAN AI AUDIT - TEST PDF")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 80, "CONFIDENTIAL & PROPRIETARY INFORMATION")
    c.line(50, height - 85, width - 50, height - 85)
    
    # Write lines of fake PII data
    c.setFont("Helvetica", 10)
    y_position = height - 110
    
    lines = FAKE_PII_TEXT.strip().splitlines()
    for line in lines:
        # Wrap simple page limit check
        if y_position < 50:
            c.showPage()
            c.setFont("Helvetica", 10)
            y_position = height - 50
            
        c.drawString(50, y_position, line)
        y_position -= 15
        
    c.save()
    print(f"Generated PDF sample: {file_path}")

if __name__ == "__main__":
    print("Generating mock files with fake PII data in the test_samples/ directory...")
    generate_txt()
    generate_csv()
    generate_pdf()
    print("All mock files successfully generated. You can now upload these to the Streamlit app for scanning.")
