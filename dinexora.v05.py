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
from atlassian import Jira
from atlassian import Confluence
import matplotlib.pyplot as plt
import cv2
import numpy as np
import logging
import seaborn as sns
from PIL import Image
from docx import Document
import io
import speech_recognition as sr
import matplotlib.pyplot as plt
import pandas as pd
import json
import requests



# ✅ MUST BE FIRST Streamlit command
st.set_page_config(page_title="Dinexora virtual QA assistant ", layout="wide")

# Setup logging
log_file_path = "test_execution.log"
logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")
# ✅ Directories
screenshot_dir = "/Users/kunnath/Projects/rfautomation/projects/UBS/Smoke/screenshots"
previous_screenshot_dir = "/Users/kunnath/Projects/rfautomation/projects/UBS/visual/previous_screenshots"
report_path = "/Users/kunnath/Projects/rfautomation/projects/UBS/visual/image_comparison_results.csv"
diff_images_dir = "/Users/kunnath/Projects/rfautomation/projects/UBS/visual/difference_images"
robot_test_file = "/Users/kunnath/Projects/rfautomation/projects/UBS/visual/dinexora.robot"
robot_output_dir = "/Users/kunnath/Projects/rfautomation/projects/UBS/visual"

# Streamlit UI
st.title("AI-Powered virtual QA assistant - Dinexora ")


# st.warning("⚠️ Please select a test suite and provide a manual file name before proceeding.")
###### BOT for the Manager#################

# 🔍 Fix NLTK Error
nltk.download("averaged_perceptron_tagger")

# 📂 Set Fixed Storage for Uploaded Documents Inside `testing_docs/`
TEMP_DIR = os.path.join(os.getcwd(), "testing_docs")
os.makedirs(TEMP_DIR, exist_ok=True)  # ✅ Create folder if not exists


# Function to recognize speech
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎤 Listening... Please speak now!")
        recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
        try:
            audio = recognizer.listen(
                source, timeout=10, phrase_time_limit=8)  # Increased timeout
            query_text = recognizer.recognize_google(audio)
            st.success(f"✅ Recognized Speech: {query_text}")
            return query_text
        except sr.WaitTimeoutError:
            st.error("❌ No speech detected. Please try again.")
            return None
        except sr.UnknownValueError:
            st.error("❌ Could not understand the audio. Please try again.")
            return None
        except sr.RequestError:
            st.error("⚠️ Speech recognition service unavailable.")
            return None


# 🔒 **User Authentication**
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False  # Default: Not logged in

if not st.session_state.user_authenticated:
    st.sidebar.title("🔑 Login to Access Chatbot")
    username = st.sidebar.text_input("Username",key="username" )
    password = st.sidebar.text_input("Password", type="password",key="password")

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
        st.sidebar.header("QA 🧠 memory")
        uploaded_files = st.sidebar.file_uploader(
            "Upload multiple PDF files", type="pdf", accept_multiple_files=True)

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

            memory = ConversationBufferMemory(
                memory_key="chat_history", return_messages=True, output_key="answer")
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
        # Initialize chatbot state
        if "chatbot_open" not in st.session_state:
            st.session_state.chatbot_open = False
        if "user_input" not in st.session_state:
             st.session_state.user_input = ""  # Store input globally

        if st.button("💬 QA Chatbot"):
            # Toggle chatbot window
            st.session_state.chatbot_open = not st.session_state.chatbot_open

        if st.session_state.chatbot_open:
            st.markdown("<h4 style='color: black;'>💬 Chat with RAGBot</h3>", unsafe_allow_html=True)

            # Option 1: Text Input
            user_input = st.text_input("Ask your uploaded PDFs a question:", value=st.session_state.user_input)
            st.session_state.user_input = user_input  # Store updated input

                # Option 2: Voice Input Button
            if st.button("🎤 Use Voice Input"):
                voice_query = recognize_speech()
                if voice_query:
                    st.session_state.user_input = voice_query  # Store voice input globally

                    # Display editable input area (this will update after voice input)
            user_input = st.text_area("📝 Edit your query before submission:", value=st.session_state.user_input)
            st.session_state.user_input = user_input  # Ensure latest value is stored

            # "Go" Button for Processing
            if st.button("Go"):
                if st.session_state.user_input.strip():  # Ensure input is not empty
                    with st.spinner("🤖 Thinking..."):
                        response = conversational_qa.invoke({"question": st.session_state.user_input})
                        st.success(response["answer"])

                        # ✅ Now "Sources Used" is a normal section, NOT inside an expander
                        st.write("📚 **Sources Used**:")
                        for doc in response["source_documents"]:
                            source = doc.metadata.get("source", "Unknown")
                            st.write(f"- {source}")
                else:
                    st.warning("Please enter a query before clicking Go.")
                    
            # Button to close chatbot
            if st.button("❌ Close Chatbot"):
                st.session_state.chatbot_open = False  # Close chatbot

# ✅ Initialize Session State Keys
required_keys = ["project_path", "suite_path", "test_creation_started", "manual_test_creation_started",
                 "test_cases_generated", "generated_test_cases", "manual_test_cases_generated", "manual_test_cases"]

for key in required_keys:
    if key not in st.session_state:
        st.session_state[key] = "" if "path" in key else False

# URL Input Field
record_url = st.text_input("Enter URL to record:", "https://dinexora.de")

# Open Browser in Normal Mode
if st.button("🌐 Open in Normal Mode", key="open_normal_browser"):
    webbrowser.open(record_url)  # ✅ Opens the default browser normally
    st.success("Opened in normal mode.")

# Open Browser in Incognito Mode
if st.button("🕶️ Open in Incognito Mode", key="open_incognito_browser"):
    if platform.system() == "Windows":
        subprocess.run(["cmd.exe", "/c", "start", "chrome",
                       "--incognito", record_url])
    elif platform.system() == "Darwin":  # ✅ macOS Fix
        subprocess.Popen(
            ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--incognito", record_url])
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
existing_projects = [p for p in os.listdir(
    BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, p))]

# Dropdown to select an existing project
selected_project = st.sidebar.selectbox(
    "Select an Existing Project:", [""] + existing_projects)

# Input to create a new project
new_project_name = st.sidebar.text_input("Or Enter New Project Name:")

if st.sidebar.button("✅ Open/Create Project", key="open_create_project"):
    if new_project_name.strip():
        st.session_state["project_path"] = os.path.join(
            BASE_DIR, new_project_name)
        os.makedirs(st.session_state["project_path"], exist_ok=True)
        st.sidebar.success(
            f"Project '{new_project_name}' created at {st.session_state['project_path']}")
    elif selected_project:
        st.session_state["project_path"] = os.path.join(
            BASE_DIR, selected_project)
        st.sidebar.success(f"Opened existing project: {selected_project}")
    else:
        st.sidebar.error(
            "⚠️ Please select an existing project or enter a new project name.")

# ✅ **Step 2: Create or Select an Existing Test Suite**
if st.session_state["project_path"]:
    st.sidebar.header("📂 Select or Create a Test Suite")

    # List existing test suites
    existing_suites = [s for s in os.listdir(st.session_state["project_path"]) if os.path.isdir(
        os.path.join(st.session_state["project_path"], s))]

    # Dropdown to select an existing test suite
    selected_suite = st.sidebar.selectbox(
        "Select an Existing Test Suite:", [""] + existing_suites)

    # Input to create a new test suite
    new_suite_name = st.sidebar.text_input("Or Enter New Test Suite Name:")

    if st.sidebar.button("📁 Open/Create Test Suite", key="open_create_suite"):
        if new_suite_name.strip():
            st.session_state["suite_path"] = os.path.join(
                st.session_state["project_path"], new_suite_name)
            os.makedirs(st.session_state["suite_path"], exist_ok=True)
            st.sidebar.success(f"Test Suite '{new_suite_name}' created.")
        elif selected_suite:
            st.session_state["suite_path"] = os.path.join(
                st.session_state["project_path"], selected_suite)
            st.sidebar.success(f"Opened existing test suite: {selected_suite}")
        else:
            st.sidebar.error("⚠️ Please select or create a test suite.")

# ✅ **Test Type Selection**
st.sidebar.header("🛠️ Test Type Selection")
test_type = st.sidebar.selectbox("Test Type", options=[
                                 "Default", "automation", 'visual', "perf", "mobile", "api", "manual"])
robot_options = st.sidebar.text_input("🔹 Robot Options", "")
browser = st.sidebar.selectbox(
    "🌐 Browser", options=["chrome", "firefox", "safari"], index=0)

# Sidebar: Paths Configuration
st.sidebar.header("📁 Configure Paths")
test_path = st.sidebar.text_input("Tests Path", "./tests")
reports_path = st.sidebar.text_input("Reports Path", "./reports")
metrics_file = os.path.abspath(os.path.join(reports_path, "metrics.html"))


   # **Allow users to upload a custom Taurus config file**
uploaded_file = st.sidebar.file_uploader("📄 Upload Taurus Test Config (YAML)", type=["yml", "yaml"], key="perf_yaml_uploader") # ✅ Assign a unique key)

    # **User-defined output directory**
output_dir = st.sidebar.text_input("📁 Output Directory", "/Users/kunnath/Projects/rfautomation/perf/perf_artifacts",key="output_dir_input")  # ✅ Unique key assigned)

    # **Default test config path (if no file uploaded)**
default_config = "/Users/kunnath/Projects/rfautomation/perf/perf_scripts/test.yml"
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
        response = ollama.generate(
            model="deepseek-coder:latest", prompt=prompt)
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
        response = ollama.generate(
            model="deepseek-coder:latest", prompt=prompt)
        return response["response"]
    except Exception as e:
        return f"Error generating test cases: {e}"


# Sidebar: Upload Test Document
st.sidebar.header("📄 Upload Test Document")
uploaded_Tfile = st.sidebar.file_uploader("Upload a Test Document", type=[
                                         "txt", "pdf", "feature", "md", "docx"], key="test_case_upload")


# ✅ **Start Robot Framework Test Case Creation (Clears Old Manual Test Cases)**
if st.sidebar.button("🤖 Start Robot Test Case Creation", key="start_robot_test_creation"):
    if uploaded_Tfile:
        # Clear previous Manual & Robot test cases
        st.session_state["manual_test_cases"] = ""
        st.session_state["manual_test_cases_generated"] = False
        st.session_state["generated_test_cases"] = ""
        st.session_state["test_cases_generated"] = False

        st.session_state["test_creation_started"] = True
        file_content = read_uploaded_file(uploaded_Tfile)

        if file_content.strip():
            with st.spinner("Generating Robot Framework test cases using AI..."):
                generated_test_cases = generate_robot_test_cases(file_content)

            st.session_state["generated_test_cases"] = generated_test_cases
            st.session_state["test_cases_generated"] = True
    else:
        st.error("⚠️ Please upload a test document first.")


# ✅ **Start Manual Test Case Creation (Clears Old Robot Test Cases)**
if st.sidebar.button("📝 Start Manual Test Case Creation", key="manual_start_test_creation"):
    if uploaded_Tfile:
        # Clear previous Manual & Robot test cases
        st.session_state["generated_test_cases"] = ""
        st.session_state["test_cases_generated"] = False
        st.session_state["manual_test_cases"] = ""
        st.session_state["manual_test_cases_generated"] = False

        st.session_state["manual_test_creation_started"] = True
        file_content = read_uploaded_file(uploaded_Tfile)

        if file_content.strip():
            with st.spinner("Generating manual test cases using AI..."):
                generated_manual_test_cases = generate_manual_test_cases(
                    file_content)

            st.session_state["manual_test_cases"] = generated_manual_test_cases
            st.session_state["manual_test_cases_generated"] = True
    else:
        st.error("⚠️ Please upload a test document first.")

# ✅ **Save & Download Robot Test Cases (.robot Format)**
if st.session_state.get("test_cases_generated", False):
    st.subheader("🤖 Generated Robot Framework Test Cases")

    # Display test cases in a text area for editing
    editable_test_cases = st.text_area(
        "📝 Edit Generated Test Cases", st.session_state["generated_test_cases"], height=400, key="edit_robot_test_cases")

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
    manual_test_cases_text = st.text_area(
        "📝 Edit Manual Test Cases", st.session_state["manual_test_cases"], height=400, key="edit_manual_test_cases")

    # ✅ Save Manual Test Cases in CSV Format
    if st.button("💾 Save & Download Manual Test Cases (CSV)", key="save_manual_test_cases"):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        manual_file_name = f"manual_test_cases_{timestamp}.csv"
        manual_file_path = os.path.join(test_path, manual_file_name)

        # Convert text to DataFrame (Splitting by lines & assuming "|" as a delimiter)
        test_case_lines = [line.split(
            "|") for line in manual_test_cases_text.strip().split("\n") if "|" in line]

        if test_case_lines:
            df = pd.DataFrame(test_case_lines[1:], columns=[
                              col.strip() for col in test_case_lines[0]])

            # Save as CSV
            df.to_csv(manual_file_path, index=False, encoding="utf-8")
            st.success(
                f"✅ Manual test cases saved successfully: {manual_file_path}")

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
#extension_url = "https://chromewebstore.google.com/detail/robotcorder/ifiilbfgcemdapeibjfohnfpfmfblmpd?hl=en"
extension_url ="https://github.com/kunnath/Dirobo/blob/main/run.sh"

st.sidebar.header("🎥 Test Recorder")

if st.sidebar.button("📹 Start Test Recording"):
    webbrowser.open(extension_url)  # ✅ Opens the default web browser normally
    st.success("Please install RoboRecorder and record your test flow.")


# Function to list available test suites (directories)
def get_test_suites(base_dir):
    if os.path.exists(base_dir):
        return [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    return []


# Get list of test suites dynamically
available_suites = get_test_suites(BASE_DIR)

# Allow user to select an existing suite or enter a new one
selected_suite = st.selectbox(
    "📁 Select or Create a Test Suite", available_suites + ["➕ Create New"], index=None)

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
    st.warning(
        "⚠️ Please select or create a test suite and provide a valid file name before proceeding.")


# JIRA Configuration
st.sidebar.header("🔹 JIRA & Confluence Integration")
if st.sidebar.button("Configure JIRA Connection"):
    st.session_state["show_jira_form"] = True

if "show_jira_form" in st.session_state and st.session_state["show_jira_form"]:
    st.subheader("🔗 Connect to JIRA")
    jira_url = st.text_input("JIRA URL", "https://aikunnath.atlassian.net")
    jira_user = st.text_input("JIRA User", "aikunnath@gmail.com")
    jira_api_token = st.text_input("JIRA API Token", type="password")

    if st.button("Connect to JIRA"):
        if jira_url and jira_user and jira_api_token:
            st.session_state["jira"] = Jira(
                url=jira_url, username=jira_user, password=jira_api_token, cloud=True)
            st.success("✅ Connected to JIRA successfully!")
        else:
            st.error("⚠️ Please fill in all fields.")

    jira_id = st.text_input("Enter JIRA Issue ID")
    if st.button("Fetch JIRA Details"):
        if jira_id:
            try:
                if "jira" in st.session_state:
                    jira = st.session_state["jira"]
                    issue = jira.issue(jira_id)
                    fields = issue.get("fields", {})
                    details = {
                        "JIRA ID": issue.get("key", "N/A"),
                        "Summary": fields.get("summary", "N/A"),
                        "Description": fields.get("description", "N/A"),
                        "Issue Type": fields.get("issuetype", {}).get("name", "N/A"),
                        "Status": fields.get("status", {}).get("name", "N/A"),
                        "Priority": fields.get("priority", {}).get("name", "N/A"),
                        "Assignee": fields.get("assignee", {}).get("displayName", "Unassigned") if fields.get("assignee") else "Unassigned",
                        "Reporter": fields.get("reporter", {}).get("displayName", "N/A") if fields.get("reporter") else "N/A",
                        "Created": fields.get("created", "N/A")
                    }
                    st.json(details)
                else:
                    st.error("⚠️ Please connect to JIRA first.")
            except Exception as e:
                st.error(f"⚠️ Error fetching JIRA details: {e}")


# Confluence Configuration
st.sidebar.header("📄 Confluence Integration")
if st.sidebar.button("Configure Confluence Connection"):
    st.session_state["show_confluence_form"] = True

if "show_confluence_form" in st.session_state and st.session_state["show_confluence_form"]:
    st.subheader("🔗 Connect to Confluence")
    confluence_url = st.text_input(
        "Confluence URL", "https://aikunnath.atlassian.net/wiki")
    confluence_user = st.text_input("Confluence User", "aikunnath@gmail.com")
    confluence_api_token = st.text_input(
        "Confluence API Token", type="password")

    if st.button("Connect to Confluence"):
        if confluence_url and confluence_user and confluence_api_token:
            st.session_state["confluence"] = Confluence(
                url=confluence_url,
                username=confluence_user,
                password=confluence_api_token,
                cloud=True
            )
            st.success("✅ Connected to Confluence successfully!")
        else:
            st.error("⚠️ Please fill in all fields.")


def fetch_confluence_page(confluence, page_title, space_key):
    try:
        page = confluence.get_page_by_title(
            space=space_key, title=page_title, expand="body.storage")

        if not page:
            st.warning(
                f"⚠️ No document found with title: {page_title} in space: {space_key}")
            return None

        details = {
            "Page ID": page.get("id", "N/A"),
            "Title": page.get("title", "N/A"),
            "Space": space_key,
            "Created": page.get("history", {}).get("createdDate", "N/A"),
            "Last Modified": page.get("version", {}).get("when", "N/A"),
            "Content": page.get("body", {}).get("storage", {}).get("value", "N/A"),
        }

        return details
    except Exception as e:
        st.error(f"⚠️ Error fetching Confluence page: {e}")
        return None


st.subheader("📄 Search Confluence Documents")
page_title = st.text_input("Enter Confluence Page Title:")
space_key = st.text_input("Enter Confluence Space Key:")

if st.button("Fetch Confluence Page"):
    if "confluence" in st.session_state:
        confluence = st.session_state["confluence"]
        confluence_details = fetch_confluence_page(
            confluence, page_title, space_key)

        if confluence_details:
            st.json(confluence_details)
    else:
        st.error("⚠️ Please connect to Confluence first.")


# ✅ Visual Testing & AI Analytics with Robot Framework

logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")


# ✅ Function to Compare Two Images and Generate Difference Images
def compare_images(img1_path, img2_path, diff_path):
    """Compare two images and return the percentage difference, saving a difference image."""
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        return None

    # Convert images to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Compute absolute difference
    diff = cv2.absdiff(gray1, gray2)
    _, diff = cv2.threshold(diff, 50, 255, cv2.THRESH_BINARY)

    # Save difference image
    cv2.imwrite(diff_path, diff)

    # Calculate the percentage of different pixels
    difference_percentage = np.sum(diff > 0) / diff.size * 100
    return round(difference_percentage, 2)


def generate_scatter_plot():

    if not os.path.exists(report_path):
        st.warning("No visual difference report found.")
        return

    df = pd.read_csv(report_path)

    if df.empty:
        st.warning("No differences detected.")
        return

    # Scatter plot
    plt.figure(figsize=(12, 6))
    plt.scatter(df["Page"], df["Difference"], c=df["Difference"],
                cmap="coolwarm", edgecolors="black")
    plt.xticks(rotation=90)
    plt.xlabel("Page")
    plt.ylabel("Visual Difference (%)")
    plt.title("Visual Differences Across Pages")
    plt.colorbar(label="Difference Intensity")

    st.pyplot(plt)


# ✅ Function to Generate Visual Metrics Report
def generate_visual_metrics():
    if not os.path.exists(report_path):
        st.warning(
            "Screenshot directories not found. Ensure both current and previous screenshots exist.")
        return

    df = pd.read_csv(report_path)
    df = df.sort_values(by="Difference", ascending=False)
    visualize_test_results(df)

    # Display only difference image URLs
    st.markdown("### 🔍 **Visual Differences Detected**")
    for file in os.listdir(diff_images_dir):
        diff_path = os.path.join(diff_images_dir, file)
        if os.path.exists(diff_path):
            file_url = f"file://{diff_path}"
            st.write(file_url)


# ✅ Function to Execute Automation Tests

def run_automation_test():
    st.write(f"Running `{test_type}` tests in {browser} browser...")
    command = [
        "robot",
        "--loglevel", "DEBUG",
        "--outputDir", reports_path,
        "--variable", f"BROWSER:{browser}",
        "--variable", "OPTIONS:--incognito"
    ]

    if robot_options.strip():
        command.extend(robot_options.split())
    command.append(test_path)

    try:
        subprocess.run(command, check=True, text=True, capture_output=True)
        st.success("🎉 Test execution completed!")
        time.sleep(2)
        # ✅ Generate Metrics Report
        st.write("📊 Generating test metrics report...")
        metrics_command = ["robotmetrics", "-M",metrics_file, "--inputpath", reports_path]
        subprocess.run(metrics_command, check=True,
                       text=True, capture_output=True)
        st.success("📈 Metrics report generated successfully!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Test execution failed: {e}")

    # Wait for 2 seconds before generating the metrics report


# ✅ Function to Execute Robot Framework Visual Tests
def run_visual_test():
    test_command = ["robot", "--outputDir", robot_output_dir, robot_test_file]
    try:
        subprocess.run(test_command, check=True,
                       text=True, capture_output=True)
        st.success("✅ Visual Testing Completed Successfully!")
        # Option to select visualization type
        # visualization_type = st.selectbox("Select Visualization Type", ["Bar Chart", "Heatmap", "Scatter Plot"], index=0)
        generate_visual_metrics()
    except subprocess.CalledProcessError as e:
        logging.error(f"Visual Testing failed: {e}")
        st.error("❌ Visual Testing Failed! Check logs for details.")
        

# ✅ Define Performance Test Execution
def run_perf_test():
    """Runs a performance test using Taurus (bzt) with live logging."""
    
    #test_config = "/Users/kunnath/Projects/rfautomation/perf/perf_scripts/test.yml"
    #output_dir = "/Users/kunnath/Projects/rfautomation/perf/perf_artifacts"
    
    # **Allow users to upload a custom Taurus config file**
    uploaded_file = st.sidebar.file_uploader("📄 Upload Taurus Test Config (YAML)", type=["yml", "yaml"])

    # **User-defined output directory**
    output_dir = st.sidebar.text_input("📁 Output Directory", "/Users/kunnath/Projects/rfautomation/perf/perf_artifacts")

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    test_command = ["bzt", uploaded_file, "-o", f"settings.artifacts-dir={output_dir}"]

    with st.spinner("🚀 Running Performance Test..."):
        try:
            process = subprocess.Popen(
                test_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
            )

            st.subheader("📜 Live Logs:")
            logs_box = st.empty()  # ✅ Use a single Streamlit element for logs

            logs = []  # ✅ Store logs in a list to update in batches

            # ✅ Stream logs in real-time
            for line in iter(process.stdout.readline, ''):
                logs.append(line)
                logs_box.text_area("Live Logs", "".join(logs), height=250)

            process.stdout.close()
            process.wait()

            if process.returncode == 0:
                st.success("✅ Performance Testing Completed Successfully!")
                show_perf_metrics(output_dir)  # ✅ Visualize Performance Results
            else:
                st.error("❌ Performance Test Failed! Check logs.")
                st.text_area("Error Log", process.stderr.read(), height=200)

        except subprocess.CalledProcessError as e:
            st.error(f"⚠️ Performance Test Execution Error: {e}")


# ✅ Define Function to Visualize Performance Results
def show_perf_metrics(output_dir):
    """Reads Taurus (bzt) results and visualizes performance metrics."""
    
    result_file = os.path.join(output_dir, "kpi.jtl")  # Taurus JMeter-style log file
    


    if not os.path.exists(result_file):
        st.warning("⚠️ No KPI report found. Ensure Taurus generated logs.")
        return

    # Load KPI Data
    df = pd.read_csv(result_file, delimiter=",", names=["Timestamp", "Label", "Response Time", "Latency", "Error Count"], skiprows=1)

    # ✅ Handle Non-Numeric Values in Timestamp Column
    df = df[pd.to_numeric(df["Timestamp"], errors="coerce").notna()]  # Remove invalid timestamps

    # ✅ Convert Timestamp to Datetime Format
    df["Timestamp"] = pd.to_datetime(df["Timestamp"].astype(float), unit="ms", errors="coerce")

    # ✅ Drop Rows with NaT (Invalid Datetime)
    df = df.dropna(subset=["Timestamp"])

    # ✅ Display Metrics Summary
    st.subheader("📊 Performance Test Summary")
    st.write(df.describe())

    # ✅ Plot Response Time Over Time
    st.subheader("📈 Response Time Trend")
    st.line_chart(df.set_index("Timestamp")["Response Time"])

    # ✅ Plot Errors Over Time
    st.subheader("🚨 Error Rate Trend")
    st.bar_chart(df.set_index("Timestamp")["Error Count"])

    # ✅ Plot Latency Distribution
   # st.subheader("⏳ Latency Distribution")
    #st.hist_chart(df["Latency"])
    st.bar_chart(df["Latency"]) 
    
    st.subheader("⏳ Latency Distribution")

    fig, ax = plt.subplots()
    ax.hist(df["Latency"], bins=20, edgecolor="black")  # ✅ Creates a histogram with 20 bins
    ax.set_xlabel("Latency (ms)")
    ax.set_ylabel("Frequency")
    ax.set_title("Latency Distribution")

    st.pyplot(fig) 


st.sidebar.header("Test Plan Chatbot")
llm = Ollama(model="deepseek-r1:1.5b")

# Function to generate a Word document
def create_word_document(content, filename):
    doc = Document()
    doc.add_heading("Test Plan", level=1)

    for section in content.split("\n"):
        if section.strip():
            doc.add_paragraph(section)

    # Save to an in-memory buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer, filename


# Sidebar button to start chatbot
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

if st.sidebar.button("Generate Test Plan", key="start_chatbot"):
    st.session_state.chat_started = True

if st.session_state.chat_started:
    st.write("Welcome! Please select the type of test plan you want.")

    # User selects test plan type
    test_plan_type = st.selectbox(
        "Choose the test plan type:",
        ["Functional", "Regression", "Performance",
            "Security", "Usability", "Compatibility"],
        key="test_plan_type"
    )

    if test_plan_type:
        # Generate a test plan dynamically based on the selected type
        file_content = read_uploaded_file(uploaded_Tfile)
        test_plan_prompt = f"""
        Generate a detailed {test_plan_type} Test Plan including the following sections:
        - Test Plan Type: {test_plan_type}
        - Objectives
        - Scope
        - Identified Risks
        - Mitigation Strategies
        - Test Environment
        - Testing Tools
        - Test Execution Approach
        - Additional Notes
        **Additional Information from Uploaded File:**
        {file_content if file_content else "No additional file content provided."}

        The test plan should be professional and structured.
        """
        

        st.session_state.generated_test_plan = llm.invoke(test_plan_prompt)

        # Display Generated Test Plan
        st.subheader(f"Generated {test_plan_type} Test Plan")
        st.write(st.session_state.generated_test_plan)

        # Create and provide download option for Word document
        word_buffer, word_filename = create_word_document(
            st.session_state.generated_test_plan, f"{test_plan_type}_test_plan.docx")
        st.download_button("Download Test Plan as Word Document", word_buffer,
                           file_name=word_filename, key="download_test_plan_word")

    # Ask user if they want modifications
    if "generated_test_plan" in st.session_state:
        st.subheader("Do you want to modify the test plan?")
        modify_prompt = st.text_area(
            "Tell the chatbot what you want to modify (e.g., 'Make the risk analysis more detailed')", key="modify_prompt")

        if st.button("Modify Test Plan", key="modify_test_plan"):
            modify_response = llm.invoke(
                f"Modify the {test_plan_type} test plan based on this request: {modify_prompt}\n\nHere is the current test plan:\n{st.session_state.generated_test_plan}")
            st.session_state.modified_test_plan = modify_response
            st.write(f"Chatbot: {modify_response}")

            # Create and provide download option for the modified Word document
            modified_word_buffer, modified_word_filename = create_word_document(
                st.session_state.modified_test_plan, f"{test_plan_type}_modified_test_plan.docx")
            st.download_button("Download Modified Test Plan as Word Document", modified_word_buffer,
                               file_name=modified_word_filename, key="download_modified_test_plan_word")

# ✅ Streamlit UI Components
#st.title("AI-Powered Visual Testing & Regression Analysis")
st.sidebar.header("📸 Visual Testing & AI Analytics")
st.sidebar.write(
    "This feature performs visual regression testing using Robot Framework and Selenium.")


# ✅ Generic Function to Visualize Test Results
def visualize_test_results(df):
    if df.empty:
        st.warning("✅ No differences detected.")
        return

    # Option to select visualization type
    visualization_type = st.selectbox("Select Visualization Type", [
                                      "Heatmap", "Bar Chart", "Scatter Plot"], index=0)

    if visualization_type == "Heatmap":
        plt.figure(figsize=(12, 8))
        sns.heatmap(df[["Difference"]].T, annot=True,
                    cmap="coolwarm", cbar=True, xticklabels=df["Page"])
        plt.xticks(rotation=90)
        plt.title("Visual Regression Testing Heatmap")
        st.pyplot(plt)

    elif visualization_type == "Bar Chart":
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(df["Page"], df["Difference"], color='skyblue')
        ax.set_xlabel("Page")
        ax.set_ylabel("Difference (%)")
        ax.set_title("Visual Regression Testing Report")
        ax.set_xticklabels(df["Page"], rotation=45, ha='right')
        ax.grid()
        st.pyplot(fig)

    elif visualization_type == "Scatter Plot":
        plt.figure(figsize=(12, 6))
        plt.scatter(df["Page"], df["Difference"],
                    c=df["Difference"], cmap="coolwarm", edgecolors="black")
        plt.xticks(rotation=90)
        plt.xlabel("Page")
        plt.ylabel("Visual Difference (%)")
        plt.title("Visual Differences Across Pages")
        plt.colorbar(label="Difference Intensity")
        st.pyplot(plt)
        



# Streamlit UI
st.title("API Validation & Analysis")


# User input for multiple API requests
num_requests = st.number_input("Enter Number of API Requests:", min_value=1, max_value=10, value=1, step=1, key="num_requests")

api_details = []
response_store = {}  # Store API responses for mapping

for i in range(num_requests):
    st.subheader(f"API Request {i+1}")
    api_url = st.text_input(f"Enter API URL {i+1}:", f"https://jsonplaceholder.typicode.com/posts/{i+1}", key=f"api_url_{i}")
    http_method = st.selectbox(f"Select HTTP Method {i+1}:", ["GET", "POST", "PUT", "DELETE"], key=f"http_method_{i}")
    headers_input = st.text_area(f"Enter Headers {i+1} (JSON format):", "{}", key=f"headers_{i}")
    body_input = st.text_area(f"Enter Body {i+1} (JSON format, optional, use {{response['key']}} for mapping):", "{}", key=f"body_{i}")
    expected_status_code = st.number_input(f"Enter Expected HTTP Status Code {i+1}:", min_value=100, max_value=599, value=200, step=1, key=f"expected_status_code_{i}")
    
    api_details.append({
        "url": api_url,
        "method": http_method,
        "headers": headers_input,
        "body": body_input,
        "expected_status": expected_status_code
    })

# Fetch API Response

# Fetch API Response
def get_api_response(api_url, http_method, headers, body):
    start_time = time.time()
    try:
        headers = json.loads(headers)
        body = json.loads(body)
        if http_method == "GET":
            response = requests.get(api_url, headers=headers)
        elif http_method == "POST":
            response = requests.post(api_url, headers=headers, json=body)
        elif http_method == "PUT":
            response = requests.put(api_url, headers=headers, json=body)
        elif http_method == "DELETE":
            response = requests.delete(api_url, headers=headers)
        else:
            return None, "Invalid HTTP method", 0
    except requests.exceptions.RequestException as e:
        return None, f"Request Error: {str(e)}", 0
    except json.JSONDecodeError:
        return None, "Invalid JSON format in headers or body", 0
    
    end_time = time.time()
    response_time = (end_time - start_time) * 1000
    return response.json(), response.status_code, response_time

# Validate API Response using DeepSeek-Coder with Ollama

# Validate API Response using DeepSeek-Coder with Ollama
def validate_api_with_deepseek(api_response, status_code, expected_status_code):
    prompt = f"""
    You are an expert API validator. Analyze the following API response and check:
    - If the response follows the expected JSON structure.
    - If the status code is correct (Expected: {expected_status_code}, Received: {status_code}).
    - If any anomalies are found.

    API Response:
    Status Code: {status_code}
    Response JSON: {json.dumps(api_response, indent=2)}

    Provide a structured validation report.
    """

    response = ollama.chat(
        model="deepseek-coder",
        messages=[
            {"role": "system", "content": "You are an expert in API validation."},
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]



# Run API Test
# Run API Test
def run_api_test():
    reports = []
    for api in api_details:
        # Resolve dynamic mapping in request body
        body = api["body"]
        for key, value in response_store.items():
            body = body.replace(f"{{response['{key}']}}", str(value))
        
        api_response, status_code, response_time = get_api_response(api["url"], api["method"], api["headers"], body)
        if api_response is None:
            st.error(f"Failed to make the request for {api['url']}: {status_code}")
            continue
        
        # Store API response for future mappings
        response_store.update(api_response)
        
        validation_result = validate_api_with_deepseek(api_response, status_code, api["expected_status"])
        
        report_data = {
            "API Endpoint": [api["url"]],
            "HTTP Method": [api["method"]],
            "Expected HTTP Status Code": [api["expected_status"]],
            "Received HTTP Status Code": [status_code],
            "Response Time (ms)": [response_time],
            "API Response": [json.dumps(api_response, indent=2)],
            "AI-Powered API Report": [validation_result],
            "API Performance": ["Good" if status_code == api["expected_status"] else "Mismatch Detected"]
        }
        reports.append(pd.DataFrame(report_data))
    
    if reports:
        df_report = pd.concat(reports, ignore_index=True)
        st.subheader("API Validation Report")
        st.dataframe(df_report)
        
        st.subheader("API Response Time Analysis")
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(df_report["API Endpoint"], df_report["Response Time (ms)"], color="blue")
        ax.set_ylabel("Time (ms)")
        ax.set_title("API Response Time Analysis")
        ax.set_xticklabels(df_report["API Endpoint"], rotation=45, ha="right")
        st.pyplot(fig)


        
# ✅ Run Test Execution
# Initialize session state for selected report

if "selected_report" not in st.session_state:
    st.session_state["selected_report"] = "Metrics Report"

# ✅ Run Test Execution
if st.button("🚀 Run Test", key="run_test"):
    if test_type == "automation":
        st.sidebar.header("📸 Web Automation Testing & AI Analytics")
        run_automation_test()
    elif test_type == "visual":
        st.sidebar.header("📸 Visual Testing & AI Analytics")
        run_visual_test()
    elif test_type == "perf":
        st.sidebar.header("📸 Performance Testing & AI Analytics")
        run_perf_test()
    elif test_type == "api":
        st.sidebar.header("📸 Api Testing & AI Analytics")    
        run_api_test()
    else:
        st.error("⚠️ Unknown test type. Please select a valid test type.")

    # ✅ Ensure reports refresh after test execution
    time.sleep(2)  # Wait for test execution to complete

    if st.session_state.get("suite_path"):
        available_reports = {
            "Metrics Report": "metrics.html",
            "Test Report": "report.html",
            "Execution Log": "log.html"
        }

        # ✅ Check for available reports in the execution directory
        existing_reports = {
            name: os.path.join(st.session_state["suite_path"], file)
            for name, file in available_reports.items()
            if os.path.exists(os.path.join(st.session_state["suite_path"], file))
        }

        if existing_reports:
            # ✅ Ensure "Metrics Report" is default after test execution
            if "Metrics Report" in existing_reports:
                st.session_state["selected_report"] = "Metrics Report"

# ✅ **Report Selection Section (No Page Refresh)**
if st.session_state.get("suite_path"):
    st.header("📊 Test Execution Reports")

    available_reports = {
        "Metrics Report": "metrics.html",
        "Test Report": "report.html",
        "Execution Log": "log.html"
    }

    existing_reports = {
        name: os.path.join(st.session_state["suite_path"], file)
        for name, file in available_reports.items()
        if os.path.exists(os.path.join(st.session_state["suite_path"], file))
    }

    if existing_reports:
        # ✅ User can select a report **without refreshing the page**
        selected_report = st.radio(
            "📄 Select a Report:", list(existing_reports.keys()), 
            index=list(existing_reports.keys()).index(st.session_state["selected_report"])
        )

        # ✅ Store selected report in session state
        st.session_state["selected_report"] = selected_report

        # ✅ Display the selected report
        with open(existing_reports[selected_report], "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=800, scrolling=True)

# Streamlit UI
# st.title("AI Test Plan Generator Bot")
