import streamlit as st
import pytesseract
from PIL import Image
from ollama import generate
from PyPDF2 import PdfReader
import requests
import pandas as pd
import time
import os
import re
from io import StringIO

# Configure Tesseract path (uncomment and modify for your OS if needed)
# pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Linux/Mac
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows

# Constants
DEFAULT_MODEL = "deepseek-coder"
ROBOT_TEMPLATE = """*** Settings ***
Library           SeleniumLibrary
Library           Collections

*** Variables ***
${URL}            https://example.com
${BROWSER}        chrome
${VALID_USER}     testuser
${VALID_PASS}     Test@123

*** Test Cases ***
"""

JIRA_TEMPLATE = """Test Case ID: TC-{timestamp}
Summary: {summary}
Description: {description}
Test Steps:
1. {steps}
Expected Results:
1. {expected}
Preconditions: {preconditions}
Postconditions: {postconditions}
Assignee: QA Team
Priority: P3
"""

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file with error handling."""
    try:
        pdf_reader = PdfReader(pdf_file)
        return "\n".join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        st.error(f"PDF processing error: {str(e)}")
        return None

def extract_text_from_image(image):
    """Extract text from an image with error handling."""
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        st.error(f"Image processing error: {str(e)}")
        return None

def generate_with_ollama(model, prompt, max_tokens=1000):
    """Wrapper for Ollama generate with error handling."""
    try:
        response = generate(
            model=model,
            prompt=prompt,
            options={'temperature': 0.7, 'num_predict': max_tokens}
        )
        return response['response']
    except Exception as e:
        st.error(f"Model generation error: {str(e)}")
        return None

def generate_robot_tests(ui_text, requirements, model_name):
    """Generate Robot Framework test cases."""
    prompt = f"""Generate complete Robot Framework test suite based on:
    
UI Elements:
{ui_text}

Requirements:
{requirements}

Important:
1. Include Settings, Variables, and Test Cases sections
2. Use 4-space indentation
3. Prefer id and css selectors
4. Include assertions
5. Add proper teardown
6. Use the template:
{ROBOT_TEMPLATE}"""
    
    return generate_with_ollama(model_name, prompt)

def generate_jira_test_cases(ui_text, requirements, model_name):
    """Generate JIRA-formatted test cases."""
    prompt = f"""Generate JIRA test cases based on:

UI Elements:
{ui_text}

Requirements:
{requirements}

Format:
{JIRA_TEMPLATE}

Include:
1. Clear test steps
2. Specific expected results
3. All required fields"""
    
    return generate_with_ollama(model_name, prompt)

def parse_jira_to_csv(jira_text):
    """Convert JIRA test case to CSV format."""
    data = {
        "Test Case ID": "",
        "Summary": "",
        "Description": "",
        "Test Steps": "",
        "Expected Results": "",
        "Preconditions": "",
        "Postconditions": "",
        "Assignee": "",
        "Priority": ""
    }
    
    current_field = None
    for line in jira_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check for field headers
        if ':' in line:
            field, value = line.split(':', 1)
            field = field.strip()
            if field in data:
                current_field = field
                data[current_field] = value.strip()
        elif current_field:
            data[current_field] += "\n" + line
            
    return pd.DataFrame([data])

# Streamlit UI
st.set_page_config(page_title="DI-Sculpt QA Assistant", layout="wide")
st.title("🛠️ DI-Sculpt QA Assistant")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    model_name = st.text_input("Ollama Model", value=DEFAULT_MODEL)
    st.info(f"Available models: deepseek-coder, llama3, mistral")
    
# Main tabs
tab1, tab2 = st.tabs(["Automated Test Generation", "Manual Test Creation"])

with tab1:
    st.header("🚀 Automated Test Generation")
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_image = st.file_uploader("Upload UI Screenshot", type=['png', 'jpg', 'jpeg'])
        functional_reqs = st.file_uploader("Upload Functional Requirements (PDF/TXT)", type=['pdf', 'txt'])
        
    with col2:
        test_reqs = st.text_area("Test Requirements", height=200, value="""Include:
1. Valid login test
2. Invalid login test
3. Empty field validation
4. Password masking validation""")
        
    if st.button("Generate Robot Framework Tests", key="gen_robot"):
        if uploaded_image:
            with st.spinner("Processing..."):
                # Extract text from image
                image = Image.open(uploaded_image)
                ui_text = extract_text_from_image(image)
                
                if ui_text:
                    st.subheader("Extracted UI Elements")
                    st.text(ui_text)
                    
                    # Get functional requirements
                    func_reqs_text = ""
                    if functional_reqs:
                        if functional_reqs.type == "application/pdf":
                            func_reqs_text = extract_text_from_pdf(functional_reqs)
                        else:
                            func_reqs_text = functional_reqs.read().decode("utf-8")
                    
                    # Generate tests
                    requirements = test_reqs + "\n" + func_reqs_text if func_reqs_text else test_reqs
                    robot_tests = generate_robot_tests(ui_text, requirements, model_name)
                    
                    if robot_tests:
                        st.subheader("Generated Test Suite")
                        st.code(robot_tests, language="robotframework")
                        
                        # Download option
                        st.download_button(
                            label="Download .robot File",
                            data=robot_tests,
                            file_name="generated_tests.robot",
                            mime="text/plain"
                        )
        else:
            st.warning("Please upload a UI screenshot")

with tab2:
    st.header("📝 Manual Test Creation")
    
    jira_col, manual_col = st.columns(2)
    
    with jira_col:
        st.subheader("JIRA Test Case Generator")
        jira_reqs = st.text_area("JIRA Requirements", height=150)
        
        if st.button("Generate JIRA Test Case"):
            if jira_reqs:
                with st.spinner("Generating..."):
                    jira_case = generate_jira_test_cases("", jira_reqs, model_name)
                    if jira_case:
                        st.text_area("JIRA Test Case", value=jira_case, height=300)
                        
                        # Convert to CSV
                        df = parse_jira_to_csv(jira_case)
                        csv = df.to_csv(index=False)
                        
                        st.download_button(
                            label="Download as CSV",
                            data=csv,
                            file_name="jira_test_case.csv",
                            mime="text/csv"
                        )
    
    with manual_col:
        st.subheader("Manual Test Case Builder")
        test_title = st.text_input("Test Case Title")
        test_steps = st.text_area("Test Steps (one per line)", height=100)
        expected = st.text_area("Expected Results (one per line)", height=100)
        
        if st.button("Create Manual Test"):
            if test_title and test_steps and expected:
                steps_list = [step for step in test_steps.split('\n') if step.strip()]
                expects_list = [exp for exp in expected.split('\n') if exp.strip()]
                
                steps = "\n".join([f"    {i+1}. {step}" for i, step in enumerate(steps_list)])
                expects = "\n".join([f"    {i+1}. {exp}" for i, exp in enumerate(expects_list)])
                
                manual_test = f"""*** Test Cases ***
                {test_title}
                    [Documentation]    Manual test case
                    [Tags]            manual
                    
                    Test Steps:
                {steps}
                    
                    Expected Results:
                {expects}"""
                                
                st.code(manual_test, language="robotframework")
            else:
                st.warning("Please fill all fields")

# Footer
st.markdown("---")
st.caption("DI-Sculpt QA Assistant v1.0 | Powered by Ollama")