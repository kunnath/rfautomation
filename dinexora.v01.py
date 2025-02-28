import os
import streamlit as st
import subprocess
import ollama
import logging
import time
import webbrowser
import fitz  # PyMuPDF for PDF extraction
import docx  # Required for DOCX file reading
import pandas as pd  # Required for test case table conversion

# Setup logging
log_file_path = "test_execution.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Streamlit UI
st.title("🚀 AI-Powered Test Automation - Dinexora 🚀")

# Sidebar: Execution Mode
st.sidebar.header("⚙️ Execution Mode")
execution_mode = st.sidebar.radio("Choose Execution Mode:", ["Local", "Docker"])

# Sidebar: Test Type Selection
st.sidebar.header("🛠️ Test Type Selection")
test_type = st.sidebar.selectbox("Test Type", options=["Default", "automation", "perf", "mobile", "api", "manual"])
robot_options = st.sidebar.text_input("🔹 Robot Options", "")
browser = st.sidebar.selectbox("🌐 Browser", options=["chrome", "firefox", "safari"], index=0)

# Sidebar: Paths Configuration
st.sidebar.header("📁 Configure Paths")
test_path = st.sidebar.text_input("Tests Path", "./tests")
reports_path = st.sidebar.text_input("Reports Path", "./reports")
metrics_file = os.path.abspath(os.path.join(reports_path, "metrics.html"))


# Ensure required directories exist
os.makedirs(test_path, exist_ok=True)
os.makedirs(reports_path, exist_ok=True)

# Sidebar: Upload Test Document
st.sidebar.header("📄 Upload Test Document")
uploaded_file = st.sidebar.file_uploader("Upload a Test Document", type=["txt", "pdf", "feature", "md", "docx"])

# Ensure session state variables exist
for key in ["test_creation_started", "manual_test_creation_started", "test_cases_generated", 
            "generated_test_cases", "manual_test_cases_generated", "manual_test_cases"]:
    if key not in st.session_state:
        st.session_state[key] = False if "generated" in key else ""

# ✅ Function to Read Uploaded File Content
def read_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        return uploaded_file.read().decode("utf-8")
    return ""

# ✅ AI-Generated Test Cases
def generate_robot_test_cases(file_content):
    prompt = f"""
    Convert the following document into Robot Framework test cases.

    {file_content}

    - Use proper Robot Framework syntax.
    - Include *** Settings ***, *** Test Cases ***, and *** Keywords *** sections.
    """

    try:
        response = ollama.generate(model="deepseek-coder:latest", prompt=prompt)
        return response["response"]
    except Exception as e:
        logging.error(f"Ollama API Error: {e}")
        return "⚠️ AI Processing Error."
    

# ✅ Function to Generate **Manual Test Cases** Using AI
def generate_manual_test_cases(file_content):
    prompt = f"""
    You are a software testing expert. Generate detailed test cases for an application based on the following requirements:

    {file_content}

    Provide the test cases in the following structured format:

    | Test Case ID | Test Case Description         | Preconditions                | Test Steps                                                                 | Test Data                | Expected Result                          |
    |--------------|-------------------------------|------------------------------|-----------------------------------------------------------------------------|--------------------------|------------------------------------------|
    | TC_001      | Verify functionality X        | Precondition details         | 1. Step 1 <br> 2. Step 2 <br> 3. Step 3                                      | Input data               | Expected outcome                         |
    """

    try:
        response = ollama.generate(model="deepseek-coder:latest", prompt=prompt)
        return response["response"]
    except Exception as e:
        return f"Error generating test cases: {e}"



# # ✅ Function to Generate **Manual Test Cases** Using AI
# def generate_manual_test_cases(file_content):
#     prompt = f"""
#     You are a software testing expert. Generate detailed test cases for an application based on the following requirements:

#     {file_content}

#     Provide the test cases in the following structured format:

#     | Test Case ID | Description | Precondition | Step | Input | Expected Output |
#     |--------------|------------|--------------|------|-------|----------------|
#     | TC_001      | Verify login | User exists | 1. Open app <br> 2. Enter credentials <br> 3. Click login | User: admin <br> Pass: pass123 | User should log in |
#     """

#     try:
#         response = ollama.generate(model="deepseek-coder:latest", prompt=prompt)
#         return response["response"]
#     except Exception as e:
#         return f"Error generating test cases: {e}"

# ✅ Function to Clean AI-Generated Tables & Fix Column Issues
def clean_test_case_table(raw_text):
    """Cleans AI-generated test cases and ensures all rows have the same column count."""
    rows = raw_text.strip().split("\n")
    
    # Extract valid rows (skip headers and dividers)
    valid_rows = [row.split("|")[1:-1] for row in rows if "|" in row and len(row.split("|")) > 2]

    if not valid_rows:
        return None, None  # Return None if no valid data found

    # Remove extra spaces & empty column names
    cleaned_rows = [[cell.strip() for cell in row if cell.strip()] for row in valid_rows]

    # Ensure unique column names
    columns = cleaned_rows[0]
    seen = set()
    unique_columns = []
    for col in columns:
        new_col = col
        counter = 1
        while new_col in seen:
            new_col = f"{col}_{counter}"
            counter += 1
        seen.add(new_col)
        unique_columns.append(new_col)

    return cleaned_rows[1:], unique_columns  # Return cleaned rows & unique columns


# ✅ **Start Robot Framework Test Case Creation (Clears Old Manual Test Cases)**
if st.sidebar.button("🤖 Start Robot Test Case Creation", key="start_robot_test_creation"):
    if uploaded_file:
        # Clear previous Manual & Robot test cases
        st.session_state["manual_test_cases"] = ""
        st.session_state["manual_test_cases_generated"] = False
        st.session_state["generated_test_cases"] = ""
        st.session_state["test_cases_generated"] = False

        st.session_state["test_creation_started"] = True
        file_content = read_uploaded_file(uploaded_file)

        if file_content.strip():
            with st.spinner("Generating Robot Framework test cases using AI..."):
                generated_test_cases = generate_robot_test_cases(file_content)
            
            st.session_state["generated_test_cases"] = generated_test_cases
            st.session_state["test_cases_generated"] = True
    else:
        st.error("⚠️ Please upload a test document first.")

# ✅ **Start Manual Test Case Creation (Clears Old Robot Test Cases)**
if st.sidebar.button("📝 Start Manual Test Case Creation", key="manual_start_test_creation"):
    if uploaded_file:
        # Clear previous Manual & Robot test cases
        st.session_state["generated_test_cases"] = ""
        st.session_state["test_cases_generated"] = False
        st.session_state["manual_test_cases"] = ""
        st.session_state["manual_test_cases_generated"] = False

        st.session_state["manual_test_creation_started"] = True
        file_content = read_uploaded_file(uploaded_file)

        if file_content.strip():
            with st.spinner("Generating manual test cases using AI..."):
                generated_manual_test_cases = generate_manual_test_cases(file_content)
            
            st.session_state["manual_test_cases"] = generated_manual_test_cases
            st.session_state["manual_test_cases_generated"] = True
    else:
        st.error("⚠️ Please upload a test document first.")

# ✅ **Save & Download Robot Test Cases (.robot Format)**
if st.session_state.get("test_cases_generated", False):
    st.subheader("🤖 Generated Robot Framework Test Cases")
    
    # Display test cases in a text area for editing
    editable_test_cases = st.text_area("📝 Edit Generated Test Cases", st.session_state["generated_test_cases"], height=400, key="edit_robot_test_cases")

    # ✅ Save Robot Test Cases in .robot Format
    if st.button("💾 Save & Download Robot Test Cases (.robot)", key="save_robot_test_cases"):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        robot_file_name = f"robot_test_cases_{timestamp}.robot"
        robot_file_path = os.path.join(test_path, robot_file_name)

        # Save as .robot file
        with open(robot_file_path, "w", encoding="utf-8") as f:
            f.write(editable_test_cases)

        st.success(f"✅ Robot test cases saved successfully: {robot_file_path}")

        # Provide Download Button
        st.download_button(
            label="📥 Download .robot File",
            data=editable_test_cases,
            file_name=robot_file_name,
            mime="text/plain"
        )

# ✅ **Save & Download Manual Test Cases (CSV Format)**
if st.session_state.get("manual_test_cases_generated", False):
    st.subheader("📄 Generated Manual Test Cases")

    # Display manual test cases
    manual_test_cases_text = st.text_area("📝 Edit Manual Test Cases", st.session_state["manual_test_cases"], height=400, key="edit_manual_test_cases")

    # ✅ Save Manual Test Cases in CSV Format
    if st.button("💾 Save & Download Manual Test Cases (CSV)", key="save_manual_test_cases"):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        manual_file_name = f"manual_test_cases_{timestamp}.csv"
        manual_file_path = os.path.join(test_path, manual_file_name)

        # Convert text to DataFrame (Splitting by lines & assuming "|" as a delimiter)
        test_case_lines = [line.split("|") for line in manual_test_cases_text.strip().split("\n") if "|" in line]
        
        if test_case_lines:
            df = pd.DataFrame(test_case_lines[1:], columns=[col.strip() for col in test_case_lines[0]])

            # Save as CSV
            df.to_csv(manual_file_path, index=False, encoding="utf-8")
            st.success(f"✅ Manual test cases saved successfully: {manual_file_path}")

            # Provide Download Button
            st.download_button(
                label="📥 Download CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=manual_file_name,
                mime="text/csv"
            )
        else:
            st.error("⚠️ No valid manual test cases found to save.")



# ✅ **Test Recording Feature**
st.sidebar.header("🎥 Test Recorder")
if st.sidebar.button("📹 Open Test Recorder"):
    webbrowser.open("https://chromewebstore.google.com/detail/robotcorder/ifiilbfgcemdapeibjfohnfpfmfblmpd?hl=en")
    st.success("Please install RoboRecorder extension to record your test steps.")

 
# URL Input Field
record_url = st.text_input("Enter URL to record:", "https://example.com")

# Open Browser Button
if st.button("🌐 Open in Browser", key="open_browser_button"):
    webbrowser.open(record_url)           

# ✅ Run Test Execution
if st.button("🚀 Run Test", key="run_test"):
    st.write(f"Running `{test_type}` tests in {browser} browser...")
    command = ["robot", "--loglevel", "DEBUG", "--outputDir", reports_path, "--variable", f"BROWSER:{browser}"]
    
    if robot_options.strip():
        command.extend(robot_options.split())
    command.append(test_path)

    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        st.success("🎉 Test execution completed!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Test execution failed: {e}")
# Wait for 2 seconds before generating the metrics report
    time.sleep(2)

    # ✅ Generate Metrics Report
    st.write("📊 Generating test metrics report...")

    # Prepare Robot Metrics command
    metrics_command = ["robotmetrics", "-M", metrics_file, "--inputpath", reports_path]

    # Execute the metrics command
    subprocess.run(metrics_command, check=True, text=True, capture_output=True)
    st.success("📈 Metrics report generated successfully!")


# ✅ **Display Reports**
st.header("📊 Test Execution Reports")
available_reports = {name: os.path.join(reports_path, file) for name, file in {
    "Metrics Report": "metrics.html",
    "Test Report": "report.html",
    "Execution Log": "log.html"
}.items() if os.path.exists(os.path.join(reports_path, file))}

if available_reports:
    selected_report = st.selectbox("📄 Select a Report:", list(available_reports.keys()))
    with open(available_reports[selected_report], "r", encoding="utf-8") as f:
        st.components.v1.html(f.read(), height=800, scrolling=True)