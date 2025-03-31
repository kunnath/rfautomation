import streamlit as st
from jira import JIRA
from ollama import generate
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
import time
from io import BytesIO



# --------------------------
# Configuration & Constants
# --------------------------
DEFAULT_MODEL = "deepseek-r1:8b"
SUPPORTED_MIME_TYPES = {
    'application/pdf': 'pdf',
    'image/png': 'image',
    'image/jpeg': 'image'
}

def init_session_state():
    session_vars = {
        'jira_conn': None,
        'current_ticket': None,
        'generated_test': None,
        'user_logged_in': False,
        'user_email': "",
        'model': DEFAULT_MODEL
    }
    for key, value in session_vars.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --------------------------
# Core Functions
# --------------------------

def configure_jira(url, email, api_key, project_key):
    try:
        jira = JIRA(
            server=url,
            basic_auth=(email, api_key),
            options={'rest_api_version': '2'},
            timeout=30
        )
        # Verify project access
        jira.project(project_key)
        st.session_state.jira_conn = jira
        st.success("✅ JIRA Connected Successfully!")
        return True
    except Exception as e:
        st.error(f"""🔐 Connection failed: {str(e)}
        1. Verify API token at https://id.atlassian.com
        2. Check project key exists
        3. Ensure user has 'Browse Projects' permission""")
        return False

def process_jira_attachment(attachment):
    """Process JIRA attachments and return extracted text"""
    try:
        file_content = attachment.get()
        if attachment.mimeType == 'application/pdf':
            return extract_pdf_text(BytesIO(file_content))
        elif attachment.mimeType.startswith('image/'):
            return pytesseract.image_to_string(Image.open(BytesIO(file_content)))
    except Exception as e:
        st.error(f"Error processing {attachment.filename}: {str(e)}")
    return ""

def extract_pdf_text(file):
    """Extract text from PDF files with error handling"""
    try:
        return "\n".join([page.extract_text() for page in PdfReader(file).pages])
    except Exception as e:
        st.error(f"PDF Error: {str(e)}")
        return ""

# --------------------------
# JIRA Ticket Processing
# --------------------------

def process_jira_ticket(ticket_id):
    """Fetch and process JIRA ticket with attachments"""
    if not st.session_state.jira_conn:
        st.error("Not connected to JIRA")
        return None
    
    try:
        ticket = st.session_state.jira_conn.issue(ticket_id)
        content = f"JIRA Ticket: {ticket.key}\n\n"
        content += f"Summary: {ticket.fields.summary}\n\n"
        content += f"Description:\n{ticket.fields.description or 'No description'}\n\n"
        
        # Process attachments
        if hasattr(ticket.fields, 'attachment') and ticket.fields.attachment:
            content += "Attachments Content:\n"
            for attachment in ticket.fields.attachment:
                attachment_content = process_jira_attachment(attachment)
                if attachment_content:
                    content += f"\n[Attachment: {attachment.filename}]\n{attachment_content}\n"
        
        return content
    except Exception as e:
        st.error(f"Failed to fetch ticket {ticket_id}: {str(e)}")
        return None

# --------------------------
# Test Generation
# --------------------------


def generate_robot_test(content, source_type="text"):
    """Generate enterprise-grade Robot Framework tests with deepseek-r1"""
    prompt = f"""Generate production-ready Robot Framework test suite from {source_type}:

{content}

Requirements:
1. Use Page Object Model pattern with resource files
2. Include Browser library (modern alternative to Selenium)
3. Implement:
   - Automatic retry mechanism
   - Smart element waiting
   - Parallel execution readiness
   - Failure screenshots
   - Environment configuration
4. Structure:
   - Common keywords
   - Test templates
   - Data-driven tests
5. Add tags for test categorization
6. Include CI/CD pipeline integration comments
7. Use external config files for environments
8. Add comprehensive documentation

Output ONLY valid Robot Framework code following Google's test automation best practices:"""

    try:
        response = generate(
            model="deepseek-r1:8b",
            prompt=prompt,
            options={
                'temperature': 0.2,
                'num_predict': 4000,
                'top_k': 40,
                'top_p': 0.9
            }
        )
        return validate_robot_code(response['response'])
    except Exception as e:
        st.error(f"🧠 Generation Error: {str(e)}")
        return None

def validate_robot_code(code):
    """Ensure generated code meets production standards"""
    required_components = [
        "*** Settings ***",
        "Library    Browser",
        "Resource    ",
        "*** Test Cases ***",
        "[Teardown]    Teardown Actions",
        "Page Object",
        "Take Screenshot"
    ]
    
    if all(component in code for component in required_components):
        return code
    st.error("Generated code missing critical components. Please regenerate.")
    return None

def generate_robot_test_(content, source_type="text"):
    prompt = f"""Generate Robot Framework test cases from {source_type}:

{content}

Required:
1. Use Page Object pattern
2. Include SeleniumLibrary keywords
3. Add setup/teardown
4. Robust CSS/XPath selectors
5. Clear assertions
6. Data-driven structure if applicable

Output ONLY valid Robot Framework code:"""

    try:
        response = generate(
            model=st.session_state.model,
            prompt=prompt,
            options={'temperature': 0.3, 'num_predict': 2500}
        )
        return validate_robot_code(response['response'])
    except Exception as e:
        st.error(f"AI Generation Error: {str(e)}")
        return None

def validate_robot_code(code):
    """Validate basic Robot Framework structure"""
    if "*** Test Cases ***" in code and "Library" in code:
        return code
    st.error("Invalid test case format generated")
    return None

# --------------------------
# UI Components
# --------------------------

def jira_input_panel():
    """JIRA ticket input and processing"""
    with st.expander("🎫 JIRA Ticket Processing", expanded=True):
        ticket_id = st.text_input("Enter JIRA Ticket ID:", "LEARNJIRA-7")
        if st.button("Process JIRA Ticket"):
            if ticket_id:
                content = process_jira_ticket(ticket_id)
                if content:
                    generate_and_display(content, f"JIRA-{ticket_id}")
            else:
                st.error("Please enter a JIRA Ticket ID")

def generate_and_display(content, source):
    """Handle test generation and display results"""
    with st.spinner(f"Generating test cases from {source}..."):
        test_case = generate_robot_test(content, source)
    
    if test_case:
        st.session_state.generated_test = test_case
        st.success("Test Case Generated Successfully!")
    else:
        st.error("Test generation failed")

# --------------------------
# Main App
# --------------------------

def main():
    st.set_page_config(
        page_title="QA Automation Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    init_session_state()
    
    # Sidebar Configuration
    with st.sidebar:
        st.title("QA Automation")
        with st.expander("🔐 JIRA Configuration", expanded=True):
            url = st.text_input("JIRA URL", "https://aikunnath.atlassian.net")
            email = st.text_input("Email", "aikunnath@gmail.com")
            api_key= "ATATT3xFfGF0cBRqV09sGLJAaHWVhFBkg-yzat1ZxFH2GyOvkApr_dmxXAndhh0s8BzxaFaLYBFdXcLWa52bFqz2rmlhQYuADRH8RiMLAN1FMaYP_uChpE0PhVrHr49u36hs027gW_Gft4AwwmBy2jKEAG_NkFWZUQohgK_lkaLlgABdJ3R6PEg=7FDAF269"
            api_key = st.text_input("API Key", type="password",value=api_key)
            project = st.text_input("Project Key", "LEARNJIRA")
           
            
            if st.button("Connect to JIRA"):
                configure_jira(url, email, api_key, project)
        
        st.session_state.model = st.selectbox(
            "AI Model",
            ["deepseek-coder:latest", "llama3.2:latest", "deepseek-r1:8b"],
            index=0
        )

    # Main Interface
    st.title("JIRA to Test Case Generator")
    jira_input_panel()

    # Results Display
    if st.session_state.generated_test:
        with st.expander("📜 Generated Test Case", expanded=True):
            st.code(st.session_state.generated_test, language="robotframework")
            st.download_button(
                "Download Test Case",
                st.session_state.generated_test,
                file_name=f"{st.session_state.current_ticket}_test.robot",
                mime="text/plain"
            )
        if st.button("Clear Results"):
            st.session_state.generated_test = None

if __name__ == "__main__":
    main()