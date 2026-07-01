import streamlit as st
import pandas as pd
from pathlib import Path
import os

# Set page configurations (Must be the first Streamlit command)
st.set_page_config(
    page_title="Guardian AI - Sensitive Data Detection & Compliance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.parsers.factory import ParserFactory
from src.detectors.manager import DetectionManager
from src.compliance.risk_classifier import RiskClassifier
from src.compliance.gemini_service import GeminiService
from src.utils.logger import setup_logger

logger = setup_logger("streamlit_app")

# Initialize services
@st.cache_resource
def get_services():
    return DetectionManager(), GeminiService()

detector_manager, gemini_service = get_services()

# --- Custom Premium CSS for Rich Aesthetics ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Overall page font override */
    html, body, [class*="css"], .stMarkdown {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
    }
    
    /* Header styling */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
    }
    
    /* Sidebar styling */
    .css-1d391tw {
        background-color: #0E1117;
    }
    
    /* Premium Glassmorphic Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
    }
    
    /* Risk Badges */
    .badge-high {
        background-color: #E74C3C;
        color: white;
        padding: 8px 16px;
        font-weight: bold;
        border-radius: 20px;
        display: inline-block;
        box-shadow: 0 0 15px rgba(231, 76, 60, 0.4);
    }
    
    .badge-medium {
        background-color: #F39C12;
        color: white;
        padding: 8px 16px;
        font-weight: bold;
        border-radius: 20px;
        display: inline-block;
        box-shadow: 0 0 15px rgba(243, 156, 18, 0.4);
    }
    
    .badge-low {
        background-color: #2ECC71;
        color: white;
        padding: 8px 16px;
        font-weight: bold;
        border-radius: 20px;
        display: inline-block;
        box-shadow: 0 0 15px rgba(46, 204, 113, 0.4);
    }
    
    /* Custom button enhancements */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        background: linear-gradient(135deg, #4A00E0 0%, #8E2DE2 100%);
        color: white !important;
        border: none;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(142, 45, 226, 0.4);
        background: linear-gradient(135deg, #5C0CE6 0%, #9B42F5 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session States to persist data between page navigation
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "findings" not in st.session_state:
    st.session_state.findings = []
if "risk_results" not in st.session_state:
    st.session_state.risk_results = None
if "compliance_report" not in st.session_state:
    st.session_state.compliance_report = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar Controls ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #8E2DE2;'>🛡️ Guardian AI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.9em; opacity: 0.7;'>Compliance & Sensitive Data Auditor</p>", unsafe_allow_html=True)
    st.write("---")
    
    # Navigation menu
    menu = st.radio(
        "Navigation Menu",
        ["📁 Upload & Scanner", "🤖 AI Compliance Summary", "💬 Ask Questions"],
        index=0
    )
    
    st.write("---")
    
    # API Status Check
    st.markdown("### API Connection Status")
    if gemini_service.is_available():
        st.markdown('<span style="color: #2ECC71; font-weight: bold;">● Gemini Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color: #E74C3C; font-weight: bold;">● Gemini Offline (.env missing API Key)</span>', unsafe_allow_html=True)
        
    st.write("---")
    st.markdown(
        """
        <div style="font-size: 0.8em; opacity: 0.6;">
            <b>Guardian AI</b> analyzes PDFs, TXT, and CSV documents to detect PII (PAN, Aadhaar, Cards), credentials (Passwords, API Keys), and custom terms, generating a complete risk vector model.
        </div>
        """, 
        unsafe_allow_html=True
    )

# --- Navigation Target: Upload & Scanner ---
if menu == "📁 Upload & Scanner":
    st.markdown("# 📁 Document Scanner")
    st.markdown("Upload a document (**PDF, CSV, TXT**) to perform a local PII/Credential scan and evaluate risk exposure.")
    st.write("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Drag and drop your file here",
            type=["pdf", "csv", "txt"],
            help="Select a file to perform scanning"
        )
        
        if uploaded_file is not None:
            # Check if this is a newly uploaded file or previously analyzed file
            if uploaded_file.name != st.session_state.uploaded_filename:
                with st.spinner("Processing file, extracting text..."):
                    try:
                        file_bytes = uploaded_file.read()
                        file_extension = Path(uploaded_file.name).suffix
                        
                        # Get appropriate parser from Factory
                        parser = ParserFactory.get_parser(file_extension)
                        document_text = parser.parse(file_bytes)
                        
                        st.session_state.document_text = document_text
                        st.session_state.uploaded_filename = uploaded_file.name
                        
                        # Clear old cached report and chat for new file
                        st.session_state.compliance_report = None
                        st.session_state.chat_history = []
                        
                        # Scan for sensitive information
                        with st.spinner("Analyzing text for sensitive data..."):
                            findings = detector_manager.scan(document_text)
                            st.session_state.findings = findings
                            
                            # Classify risk
                            risk_results = RiskClassifier.classify(findings)
                            st.session_state.risk_results = risk_results
                            
                        st.success(f"Successfully processed {uploaded_file.name}!")
                        
                    except Exception as e:
                        st.error(f"Error parsing file: {str(e)}")
                        logger.critical(f"File upload processing failed: {str(e)}")

    if st.session_state.uploaded_filename:
        # Display Risk Dashboard Panel
        risk_data = st.session_state.risk_results
        findings = st.session_state.findings
        
        # Risk levels mapping to colors and badges
        risk_level = risk_data["risk_level"]
        badge_html = ""
        if risk_level == "HIGH":
            badge_html = f'<span class="badge-high">HIGH RISK (Score: {risk_data["total_score"]})</span>'
        elif risk_level == "MEDIUM":
            badge_html = f'<span class="badge-medium">MEDIUM RISK (Score: {risk_data["total_score"]})</span>'
        else:
            badge_html = f'<span class="badge-low">LOW RISK (Score: {risk_data["total_score"]})</span>'

        with col2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### Risk Assessment Verdict")
            st.markdown(badge_html, unsafe_allow_html=True)
            st.markdown(f"<p style='margin-top: 15px;'>{risk_data['guidance']}</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.write("---")
        
        # --- Findings Summary & Visual Charts ---
        st.markdown("## Scan Results")
        
        if not findings:
            st.info("🎉 Great news! No sensitive entities or credentials were detected in this document.")
        else:
            c1, c2 = st.columns([3, 2])
            
            with c1:
                st.markdown("### Detected Sensitive Entities")
                # Format findings as DataFrame
                records = [f.to_dict() for f in findings]
                df = pd.DataFrame(records)
                
                # Format headers for display
                df.columns = ["Entity Type", "Matched Value", "Match Confidence", "Location"]
                # Convert confidence to percentage for nicer presentation
                df["Match Confidence"] = df["Match Confidence"].apply(lambda x: f"{x * 100:.1f}%")
                
                st.dataframe(df, use_container_width=True, hide_index=True)
                
                # Download findings CSV button
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Findings CSV",
                    data=csv_data,
                    file_name=f"findings_{st.session_state.uploaded_filename}.csv",
                    mime="text/csv"
                )
                
            with c2:
                st.markdown("### Risk Breakdown")
                
                # Generate simple bar chart of entity type distribution
                entity_counts = risk_data["entity_counts"]
                chart_df = pd.DataFrame(
                    list(entity_counts.items()), 
                    columns=["Entity Type", "Occurrences"]
                ).sort_values(by="Occurrences", ascending=False)
                
                st.bar_chart(chart_df.set_index("Entity Type"), use_container_width=True)
                
                # Detail justifications
                st.markdown("#### Weight Computations")
                for justification in risk_data["justifications"]:
                    st.write(f"- {justification}")
    else:
        st.info("Upload a document file to begin scanning and auditing.")

# --- Navigation Target: AI Compliance Summary ---
elif menu == "🤖 AI Compliance Summary":
    st.markdown("# 🤖 AI Compliance Summary")
    st.markdown("Generate a deep, LLM-powered compliance audit and vulnerability brief using Google Gemini.")
    st.write("---")
    
    if not st.session_state.uploaded_filename:
        st.info("⚠️ Please upload a document in the **Upload & Scanner** tab first.")
    else:
        # Check if Gemini key is set
        if not gemini_service.is_available():
            st.warning("⚠️ Gemini API is not configured. Please supply a valid `GEMINI_API_KEY` inside `.env` to execute compliance reports.")
        else:
            # Option to generate report if not cached
            if st.session_state.compliance_report is None:
                if st.button("🚀 Generate AI Compliance Report"):
                    with st.spinner("Gemini is auditing document context and local scan metrics..."):
                        report = gemini_service.generate_compliance_report(
                            st.session_state.document_text,
                            st.session_state.findings
                        )
                        st.session_state.compliance_report = report
                        
            # Show cached or generated report
            if st.session_state.compliance_report:
                st.markdown("### Audit Findings Report")
                st.markdown(
                    f"<div class='glass-card' style='padding: 30px;'>{st.session_state.compliance_report}</div>", 
                    unsafe_allow_html=True
                )
                
                # Allow download of the report
                st.download_button(
                    label="📥 Download Compliance Report (.md)",
                    data=st.session_state.compliance_report,
                    file_name=f"compliance_report_{st.session_state.uploaded_filename}.md",
                    mime="text/markdown"
                )

# --- Navigation Target: Ask Questions ---
elif menu == "💬 Ask Questions":
    st.markdown("# 💬 Audit Assistant Q&A")
    st.markdown("Ask natural language questions about the uploaded document (e.g. *'What values were flagged?'*, *'Summarize the primary purpose of the document'*).")
    st.write("---")
    
    if not st.session_state.uploaded_filename:
        st.info("⚠️ Please upload a document in the **Upload & Scanner** tab first.")
    else:
        if not gemini_service.is_available():
            st.warning("⚠️ Gemini API is offline. Q&A requires `GEMINI_API_KEY` in `.env`.")
        else:
            # Display chat history
            for chat in st.session_state.chat_history:
                role = chat["role"]
                content = chat["content"]
                
                if role == "user":
                    with st.chat_message("user"):
                        st.markdown(content)
                else:
                    with st.chat_message("assistant"):
                        st.markdown(content)
                        
            # User input box
            question = st.chat_input("Ask a question about the uploaded document:")
            
            if question:
                # Append user chat
                st.session_state.chat_history.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)
                    
                # Call Gemini QA
                with st.spinner("Retrieving document context and answering..."):
                    answer = gemini_service.ask_question(
                        st.session_state.document_text,
                        question
                    )
                    
                # Append assistant chat
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    st.rerun()  # Refresh screen to show changes
