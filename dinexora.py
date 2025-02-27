import os
import streamlit as st
import subprocess
import ollama
import logging
import re
import time

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
metrics_file = os.path.join(reports_path, "metrics.html")



# Ensure required directories exist
os.makedirs(test_path, exist_ok=True)
os.makedirs(reports_path, exist_ok=True)

# Sidebar: Upload Test Document
st.sidebar.header("📄 Upload Test Document")
uploaded_file = st.sidebar.file_uploader("Upload a Test Document", type=["txt", "feature", "md", "docx"])

# Initialize session state
if "test_cases_saved" not in st.session_state:
    st.session_state["test_cases_saved"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ✅ Read Uploaded Document
def read_uploaded_file(uploaded_file):
    try:
        return uploaded_file.read().decode("utf-8")
    except UnicodeDecodeError:
        return uploaded_file.read().decode("ISO-8859-1")

# ✅ AI-Generated Robot Framework Test Cases
def generate_robot_test_cases(file_content):
    prompt = f"""
    Convert the following document into Robot Framework test cases.

    {file_content}

    - Use proper Robot Framework syntax.
    - Include *** Settings ***, *** Test Cases ***, and *** Keywords *** sections.
    - Use best practices in test automation.
    """

    try:
        response = ollama.generate(model="deepseek-coder:latest", prompt=prompt)
        return response["response"]
    except Exception as e:
        logging.error(f"Ollama API Error: {e}")
        return "⚠️ AI Processing Error."

# ✅ Save Robot Framework Test Cases
def save_robot_test_cases(test_content):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    file_name = f"test_cases_{timestamp}.robot"
    file_path = os.path.join(test_path, file_name)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(test_content)

    return file_path

# ✅ AI Modification of Test Cases
def modify_robot_test_cases(existing_test_cases, user_prompt):
    prompt = f"""
    Modify the following Robot Framework test cases based on user request.

    Test Cases:
    {existing_test_cases}

    User Request:
    {user_prompt}

    Return a properly formatted and structured Robot Framework test script.
    """

    try:
        response = ollama.generate(model="deepseek-coder:latest", prompt=prompt)
        return response["response"]
    except Exception as e:
        logging.error(f"Ollama API Error: {e}")
        return "⚠️ AI Processing Error."

# ✅ Process Uploaded Document
if uploaded_file:
    st.success("✅ Test document uploaded successfully!")
    file_content = read_uploaded_file(uploaded_file)

    if file_content.strip():
        with st.spinner("Generating test cases using AI..."):
            generated_test_cases = generate_robot_test_cases(file_content)

        editable_test_cases = st.text_area("📝 Edit Generated Test Cases", generated_test_cases, height=400)

        if st.button("💾 Save Test Cases"):
            saved_file = save_robot_test_cases(editable_test_cases)
            if saved_file:
                st.success(f"✅ Test cases saved successfully: {saved_file}")
                st.session_state["test_cases_saved"] = True

                # Chatbot Section after saving test cases
                st.subheader("💬 AI Chatbot for Test Case Refinement")
                user_prompt = st.text_area("Tell the AI how you want to modify the test cases:")

                if st.button("✍️ Modify with AI"):
                    with st.spinner("Modifying test cases..."):
                        modified_test_cases = modify_robot_test_cases(editable_test_cases, user_prompt)

                    st.text_area("📝 Modified Test Cases", modified_test_cases, height=400)

                    if st.button("💾 Save Modified Test Cases"):
                        final_file = save_robot_test_cases(modified_test_cases)
                        if final_file:
                            st.success(f"✅ Final test cases saved successfully: {final_file}")
                            st.session_state["test_cases_saved"] = True

# ✅ Chatbot Section (only after test cases are saved)
if st.session_state.get("test_cases_saved"):
    st.markdown("## 💬 AI Test Case Assistant")
    st.write("Chat with AI for test case refinements or automation help.")

    # Display chat history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about test cases or automation..."):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI response
        with st.chat_message("assistant"):
            st.markdown("_Generating response..._")
            try:
                stream = ollama.chat(model="deepseek-coder:latest", messages=st.session_state["messages"], stream=True)
                full_response = ""
                for chunk in stream:
                    content = chunk.get("message", {}).get("content", "")
                    full_response += content
                    st.markdown(full_response + "▌")  # Live update
                st.markdown(full_response)
                st.session_state["messages"].append({"role": "assistant", "content": full_response})
            except Exception as err:
                st.error(f"Error generating response: {err}")


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