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
import platform
from langchain.document_loaders import DirectoryLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
import nltk
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# ✅ MUST BE FIRST Streamlit command
st.set_page_config(page_title="Manager Assistant", layout="wide")

# Setup logging
log_file_path = "test_execution.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Streamlit UI
st.title("AI-Powered Test Automation - Dinexora ")
#st.warning("⚠️ Please select a test suite and provide a manual file name before proceeding.")
######BOT for the Manager#################           

# 🔍 Fix NLTK Error
nltk.download("averaged_perceptron_tagger")

# 📂 Set Fixed Storage for Uploaded Documents Inside `testing_docs/`
TEMP_DIR = os.path.join(os.getcwd(), "testing_docs")
os.makedirs(TEMP_DIR, exist_ok=True)  # ✅ Create folder if not exists

# 🔒 **User Authentication**
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False  # Default: Not logged in

if not st.session_state.user_authenticated:
    st.sidebar.title("🔑 Login to Access Chatbot")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        # **Simple Hardcoded Authentication (Replace with DB or OAuth)**
        if username == "manager" and password == "admin123":
            st.session_state.user_authenticated = True
            st.success("✅ Login Successful! You can now use the chatbot.")
            st.rerun()
        else:
            st.error("❌ Incorrect username or password")

# ✅ Show Content Only After Login
if st.session_state.user_authenticated:
    # **Main Page Layout**
    col1, col2 = st.columns([3, 1])  # Chatbot (right), Other fields (left)

    with col1:  # Main UI elements
        st.title("QA 🧠 memory")
        uploaded_files = st.file_uploader("Upload multiple PDF files", type="pdf", accept_multiple_files=True)

        if uploaded_files:
            all_docs = []

            for uploaded_file in uploaded_files:
                file_path = os.path.join(TEMP_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                loader = PDFPlumberLoader(file_path)
                docs = loader.load()
                all_docs.extend(docs)

            text_splitter = SemanticChunker(HuggingFaceEmbeddings())
            documents = text_splitter.split_documents(all_docs)

            embeddings = HuggingFaceEmbeddings()
            vector_store = FAISS.from_documents(documents, embeddings)
            retriever = vector_store.as_retriever(search_kwargs={"k": 5})

            memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key="answer")
            llm = Ollama(model="deepseek-r1:1.5b")

            conversational_qa = ConversationalRetrievalChain.from_llm(
                llm=llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=True,
                output_key="answer"
            )

    # **Chatbot in Top Right Corner**
    with col2:
        if "chatbot_open" not in st.session_state:
            st.session_state.chatbot_open = False  # Default: Chatbot is closed

        if st.button("💬 QA Chatbot)"):
            st.session_state.chatbot_open = not st.session_state.chatbot_open  # Toggle chatbot window

        if st.session_state.chatbot_open:
            st.subheader("💬 Chat with RAGBot")
            user_input = st.text_input("Ask your uploaded PDFs a question:")

            if user_input:
                with st.spinner("Sri thinking.."):
                    response = conversational_qa.invoke({"question": user_input})
                    st.success(response["answer"])

                    # ✅ Now "Sources Used" is a normal section, NOT inside an expander
                    st.write("📚 **Sources Used**:")
                    for doc in response["source_documents"]:
                        source = doc.metadata.get("source", "Unknown")
                        st.write(f"- {source}")

            # Button to close chatbot
            if st.button("❌ Close Chatbot"):
                st.session_state.chatbot_open = False             
 
# ✅ Initialize Session State Keys
required_keys = ["project_path", "suite_path", "test_creation_started", "manual_test_creation_started", 
                 "test_cases_generated", "generated_test_cases", "manual_test_cases_generated", "manual_test_cases"]

for key in required_keys:
    if key not in st.session_state:
        st.session_state[key] = "" if "path" in key else False

# URL Input Field
record_url = st.text_input("Enter URL to record:", "https://example.com")

# Open Browser in Normal Mode
if st.button("🌐 Open in Normal Mode", key="open_normal_browser"):
    webbrowser.open(record_url)  # ✅ Opens the default browser normally
    st.success("Opened in normal mode.")

# Open Browser in Incognito Mode
if st.button("🕶️ Open in Incognito Mode", key="open_incognito_browser"):
    if platform.system() == "Windows":
        subprocess.run(["cmd.exe", "/c", "start", "chrome", "--incognito", record_url])
    elif platform.system() == "Darwin":  # ✅ macOS Fix
        subprocess.Popen(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--incognito", record_url])
    elif platform.system() == "Linux":
        subprocess.run(["google-chrome", "--incognito", record_url])
    else:
        st.error("Unsupported OS for launching incognito mode.")

    st.success("Opened in incognito mode.")


# ✅ **Step 1: Create or Open Existing Project**
BASE_DIR = "./projects"
os.makedirs(BASE_DIR, exist_ok=True)

st.sidebar.header("📁 Select or Create a Project")

# List existing projects
existing_projects = [p for p in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, p))]

# Dropdown to select an existing project
selected_project = st.sidebar.selectbox("Select an Existing Project:", [""] + existing_projects)

# Input to create a new project
new_project_name = st.sidebar.text_input("Or Enter New Project Name:")

if st.sidebar.button("✅ Open/Create Project", key="open_create_project"):
    if new_project_name.strip():
        st.session_state["project_path"] = os.path.join(BASE_DIR, new_project_name)
        os.makedirs(st.session_state["project_path"], exist_ok=True)
        st.sidebar.success(f"Project '{new_project_name}' created at {st.session_state['project_path']}")
    elif selected_project:
        st.session_state["project_path"] = os.path.join(BASE_DIR, selected_project)
        st.sidebar.success(f"Opened existing project: {selected_project}")
    else:
        st.sidebar.error("⚠️ Please select an existing project or enter a new project name.")

# ✅ **Step 2: Create or Select an Existing Test Suite**
if st.session_state["project_path"]:
    st.sidebar.header("📂 Select or Create a Test Suite")

    # List existing test suites
    existing_suites = [s for s in os.listdir(st.session_state["project_path"]) if os.path.isdir(os.path.join(st.session_state["project_path"], s))]

    # Dropdown to select an existing test suite
    selected_suite = st.sidebar.selectbox("Select an Existing Test Suite:", [""] + existing_suites)

    # Input to create a new test suite
    new_suite_name = st.sidebar.text_input("Or Enter New Test Suite Name:")

    if st.sidebar.button("📁 Open/Create Test Suite", key="open_create_suite"):
        if new_suite_name.strip():
            st.session_state["suite_path"] = os.path.join(st.session_state["project_path"], new_suite_name)
            os.makedirs(st.session_state["suite_path"], exist_ok=True)
            st.sidebar.success(f"Test Suite '{new_suite_name}' created.")
        elif selected_suite:
            st.session_state["suite_path"] = os.path.join(st.session_state["project_path"], selected_suite)
            st.sidebar.success(f"Opened existing test suite: {selected_suite}")
        else:
            st.sidebar.error("⚠️ Please select or create a test suite.")

# ✅ **Test Type Selection**
st.sidebar.header("🛠️ Test Type Selection")
test_type = st.sidebar.selectbox("Test Type", options=["Default", "automation", "perf", "mobile", "api", "manual"])
robot_options = st.sidebar.text_input("🔹 Robot Options", "")
browser = st.sidebar.selectbox("🌐 Browser", options=["chrome", "firefox", "safari"], index=0)

# Sidebar: Paths Configuration
st.sidebar.header("📁 Configure Paths")
test_path = st.sidebar.text_input("Tests Path", "./tests")
reports_path = st.sidebar.text_input("Reports Path", "./reports")
metrics_file = os.path.abspath(os.path.join(reports_path, "metrics.html"))

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

# Sidebar: Upload Test Document
st.sidebar.header("📄 Upload Test Document")
uploaded_file = st.sidebar.file_uploader("Upload a Test Document", type=["txt", "pdf", "feature", "md", "docx"])



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



# Define the RoboRecorder Chrome Extension URL
extension_url = "https://chromewebstore.google.com/detail/robotcorder/ifiilbfgcemdapeibjfohnfpfmfblmpd?hl=en"

st.sidebar.header("🎥 Test Recorder")

if st.sidebar.button("📹 Start Test Recording"):
    webbrowser.open(extension_url)  # ✅ Opens the default web browser normally
    st.success("Please install RoboRecorder and record your test flow.")


# # Define the RoboRecorder Chrome Extension URL
# extension_url = "https://chromewebstore.google.com/detail/robotcorder/ifiilbfgcemdapeibjfohnfpfmfblmpd?hl=en"

# st.sidebar.header("🎥 Test Recorder")

# if st.sidebar.button("📹 Start Test Recording"):
#     if platform.system() == "Windows":
#         subprocess.run(["cmd.exe", "/c", "start", "chrome", "--incognito", extension_url])
#     elif platform.system() == "Darwin":  # ✅ macOS Fix
#         subprocess.Popen(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--incognito", extension_url])
#     elif platform.system() == "Linux":
#         subprocess.run(["google-chrome", "--incognito", extension_url])
#     else:
#         st.error("Unsupported OS for launching incognito mode.")

#     st.success("Please install RoboRecorder and record your test flow.")

# ✅ Run Test Execution
if st.button("🚀 Run Test", key="run_test"):
    st.write(f"Running `{test_type}` tests in {browser} browser...")
    command = [
        "robot",
        "--loglevel", "DEBUG",
        "--outputDir", reports_path,
        "--variable", f"BROWSER:{browser}",
        "--variable", "OPTIONS:--incognito"  # Corrected syntax
    ]
    
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


# Function to list available test suites (directories)
def get_test_suites(base_dir):
    if os.path.exists(base_dir):
        return [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    return []

# Get list of test suites dynamically
available_suites = get_test_suites(BASE_DIR)

# Allow user to select an existing suite or enter a new one
selected_suite = st.selectbox("📁 Select or Create a Test Suite", available_suites + ["➕ Create New"], index=None)

# If "Create New" is selected, allow user to enter a new suite name
if selected_suite == "➕ Create New":
    new_suite_name = st.text_input("Enter New Test Suite Name")
    if new_suite_name:
        selected_suite = new_suite_name  # Assign new suite name

# Enter test case file name
manual_file_name = st.text_input("Enter CSV File Name (e.g., test_cases.csv)")

# Check if all inputs are provided before proceeding
if BASE_DIR and selected_suite and manual_file_name:
    suite_path = os.path.join(BASE_DIR, selected_suite)

    # Create new test suite directory if it doesn't exist
    if not os.path.exists(suite_path):
        os.makedirs(suite_path)  # ✅ Create the new suite directory

    csv_file_path = os.path.join(suite_path, manual_file_name)

    if st.button("📂 Open Generated Test Case"):
        if os.path.exists(csv_file_path):
            df = pd.read_csv(csv_file_path)  # Load CSV
            st.success("✅ Test cases loaded successfully!")
            st.dataframe(df)  # Show CSV in table view
        else:
            st.error(f"⚠️ No test case file found at: {csv_file_path}")
else:
    st.warning("⚠️ Please select or create a test suite and provide a valid file name before proceeding.")


# ✅ **Display Reports**
if st.session_state["suite_path"]:
    st.header("📊 Test Execution Reports")
    available_reports = {
        "Metrics Report": "metrics.html",
        "Test Report": "report.html",
        "Execution Log": "log.html"
    }

    existing_reports = {name: os.path.join(st.session_state["suite_path"], file) for name, file in available_reports.items() if os.path.exists(os.path.join(st.session_state["suite_path"], file))}

    if existing_reports:
        selected_report = st.selectbox("📄 Select a Report:", list(existing_reports.keys()))
        with open(existing_reports[selected_report], "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=800, scrolling=True)
 