import os
import streamlit as st
import subprocess
import ollama
import logging
import re
import time


# Setup logging (log errors but don't show in UI)
log_file_path = "test_execution.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Streamlit UI
st.title("🚀 AI-Powered All-in-One Test Automation Solution - Dinexora 🚀")

# Sidebar: Execution Mode
st.sidebar.header("⚙️ Execution Mode")
execution_mode = st.sidebar.radio("Choose Execution Mode:", ["Local", "Docker"])

# Sidebar: Test Type Selection
st.sidebar.header("🛠️ Test Type Selection")
test_type = st.sidebar.selectbox(
    "Test Type", options=["Default", "automation", "perf", "mobile", "api", "manual"]
)

robot_options = st.sidebar.text_input("🔹 Robot Options", "")
browser = st.sidebar.selectbox("🌐 Browser", options=["chrome", "firefox", "safari"], index=0)

# Sidebar: Paths Configuration
st.sidebar.header("📁 Configure Paths")
test_path = st.sidebar.text_input("Tests Path", "./tests")
reports_path = st.sidebar.text_input("Reports Path", "./reports")
metrics_file = os.path.join(reports_path, "metrics.html")

# Ensure required directories exist
os.makedirs(test_path, exist_ok=True)
os.makedirs(reports_path, exist_ok=True)

# Sidebar: Upload Test Document
st.sidebar.header("📄 Upload Test Document")
uploaded_file = st.sidebar.file_uploader("Upload a Test Document", type=["txt", "feature", "md", "docx"])

# ✅ Read Uploaded Document with Encoding Handling
def read_uploaded_file(uploaded_file):
    try:
        return uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        try:
            return uploaded_file.read().decode("ISO-8859-1")
        except UnicodeDecodeError:
            return uploaded_file.read().decode("Windows-1252")

# ✅ Generate Robot Framework Test Cases Using AI
def generate_robot_test_cases_from_ai(file_content):
    prompt = f"""
    You are an expert in test automation using Robot Framework.
    Extract multiple test scenarios from the following test document:

    {file_content}

    For each scenario:
    - The file should follow Robot Framework syntax.
    - Include *** Settings ***, *** Test Cases ***, and *** Keywords *** sections.
    - Use SeleniumLibrary for UI-based tests.
    - Name each test case based on the scenario title.

    Return a list of scenarios in separate sections.
    """

    try:
        response = ollama.generate(model="deepseek-coder:latest", prompt=prompt)
        return response["response"]  # Extract the generated content

    except ollama._types.ResponseError as e:
        logging.error(f"Ollama API Error: {e}")
        if "model not found" in str(e):
            subprocess.run(["ollama", "pull", "deepseek-coder:latest"], check=True)
            st.success("✅ AI Model pulled successfully! Try running the test again.")
        else:
            st.error("⚠️ AI Processing Error. Please check logs for details.")

# ✅ Save Multiple Test Cases as `.robot` Files
# ✅ Save Multiple Test Cases as `.robot` Files (Fixed Naming)
def save_robot_test_cases(test_content):
    test_scenarios = re.split(r"\n\s*\*\*\* Test Cases \*\*\*\s*\n", test_content, flags=re.MULTILINE)
    
    if len(test_scenarios) < 2:
        return []

    settings_section = test_scenarios[0]
    scenario_cases = test_scenarios[1:]

    generated_files = []
    timestamp = time.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS

    for scenario in scenario_cases:
        match = re.match(r"([^\n]+)", scenario.strip())
        if match:
            scenario_name = match.group(1).strip()

            # ✅ Shorten Scenario Name (Limit to 30 characters)
            scenario_name = re.sub(r'\W+', '_', scenario_name)[:30]

            # ✅ Append Timestamp to Ensure Uniqueness
            file_name = f"{scenario_name}_{timestamp}.robot"
            file_path = os.path.join(test_path, file_name)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write("*** Settings ***\n")
                f.write(settings_section.strip() + "\n\n")
                f.write("*** Test Cases ***\n")
                f.write(scenario.strip() + "\n")

            generated_files.append(file_path)

    return generated_files



# ✅ Process Uploaded Document
if uploaded_file:
    st.success("✅ Test document uploaded successfully!")

    file_content = read_uploaded_file(uploaded_file)

    if file_content.strip():
        with st.spinner("Generating test cases using AI..."):
            generated_test_cases = generate_robot_test_cases_from_ai(file_content)

        editable_test_cases = st.text_area("📝 Edit Generated Test Cases", generated_test_cases, height=400)

        if st.button("💾 Save Test Cases"):
            generated_files = save_robot_test_cases(editable_test_cases)
            if generated_files:
                st.success(f"✅ Generated {len(generated_files)} Robot Framework test cases!")

    else:
        st.error("⚠️ The uploaded file appears to be empty or unreadable.")

# ✅ Run Test Execution (Without Showing Errors in UI)
if st.button("🚀 Run Test"):
    st.write(f"Running `{test_type}` tests in {browser} browser...")

    command = ["robot", "--loglevel", "DEBUG", "--outputDir", reports_path, "--variable", f"BROWSER:{browser}"]

    if robot_options.strip():
        command.extend(robot_options.split())

    command.append(test_path)

    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        st.success("🎉 Test execution completed!")

        # Generate Metrics Report
        subprocess.run(["robotmetrics", "-M", metrics_file, "--inputpath", reports_path], check=True, text=True, capture_output=True)

    except subprocess.CalledProcessError as e:
        logging.error(f"Test execution failed: {e}")

# ✅ Display Reports
st.header("📊 Test Execution Reports")
available_reports = {
    "Metrics Report": os.path.join(reports_path, "metrics.html"),
    "Test Report": os.path.join(reports_path, "report.html"),
    "Execution Log": os.path.join(reports_path, "log.html"),
}

existing_reports = {name: path for name, path in available_reports.items() if os.path.exists(path)}

if existing_reports:
    selected_report = st.selectbox("📄 Select a Report:", list(existing_reports.keys()))
    selected_file = existing_reports[selected_report]

    with open(selected_file, "r", encoding="utf-8") as f:
        html_content = f.read().strip()

    if html_content:
        html_content = html_content.replace('<a ', '<a target="_self" ')
        st.components.v1.html(html_content, height=800, scrolling=True)
    else:
        st.warning(f"⚠️ The file {selected_file} is empty!")
else:
    st.error("⚠️ No reports found. Run the test first!")