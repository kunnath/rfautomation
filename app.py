import os
import subprocess
import streamlit as st

# Streamlit UI
st.title("Run Robot Framework Docker Script")

# Input fields for the script
st.sidebar.header("Script Parameters")
build_robot_docker = st.sidebar.checkbox("Build Robot Docker", False)
test_type = st.sidebar.selectbox(
    "Test Type", options=["Default", "perf", "mobile", "api", "manual"]
)
robot_options = st.sidebar.text_input("Robot Options", "")
browser = st.sidebar.selectbox("Browser", options=["chrome", "firefox", "safari"], index=0)

# Display paths
st.write("### Paths")
test_path = st.text_input("Tests Path", "./tests")
reports_path = st.text_input("Reports Path", "./reports")
artifact_store_path = st.text_input("Artifact Store Path", "./artifact_store")
variables_path = st.text_input("Variables Path", "./variables")
keywords_path = st.text_input("Keywords Path", "./keywords")

# Run the script
if st.button("Run Script"):
    st.write("Running script...")

    # Set environment variables
    env = os.environ.copy()
    env["ROBOT_OPTIONS"] = robot_options
    env["BROWSER"] = browser

    # Define the command
    script_path = "./rfdocker.sh"
    command = [script_path]

    if test_type != "Default":
        command.append(test_type)

    # Paths
    paths = {
        "tests": test_path,
        "reports": reports_path,
        "artifact_store": artifact_store_path,
        "variables": variables_path,
        "keywords": keywords_path,
    }

    # Validate paths
    for name, path in paths.items():
        if not os.path.exists(path):
            st.error(f"Path does not exist: {path}")
            st.stop()

    # Check if we need to build the Docker image
    if build_robot_docker:
        st.write("Building Robot Docker image...")
        try:
            # Run the Docker build command
            subprocess.run(
                ["docker", "build", "-t", "rfdocker:rfautomation", "."],
                check=True,
                text=True,
                capture_output=True,
            )
            st.success("Docker image built successfully!")
        except subprocess.CalledProcessError as e:
            st.error(f"Error building the Docker image: {e.stderr}")
            st.stop()
    else:
        st.write("Using existing Robot Docker image...")

    try:
        # Run the Docker container using the existing image (or newly built image)
        result = subprocess.run(
            [
                "docker", "run", "--rm", "--shm-size", "5g",
                "-v", f"{test_path}:/opt/robotframework/tests:Z",
                "-v", f"{reports_path}:/opt/robotframework/reports:Z",
                "-v", f"{artifact_store_path}:/opt/robotframework/artifact_store:Z",
                "-v", f"{variables_path}:/opt/robotframework/variables:Z",
                "-v", f"{keywords_path}:/opt/robotframework/keywords:Z",
                "-e", f"ROBOT_OPTIONS={robot_options}",
                "-e", f"BROWSER={browser}",
                "rfdocker:rfautomation",  # Use the image name
            ],
            check=False,
            capture_output=True,
            text=True,
        )

        # Output results
        st.code(result.stdout)
        if result.stderr:
            st.error(result.stderr)

        # Check if the report link is available
        report_url = os.path.join(reports_path, "metrics.html")
        if os.path.exists(report_url):
            st.success("Test report generated successfully!")

            # Provide a download button for the report
            with open(report_url, "rb") as file:
                st.download_button(
                    label="Download Report",
                    data=file,
                    file_name="metrics.html",
                    mime="text/html",
                )
        else:
            st.error("Report file not found!")

    except Exception as e:
        st.error(f"Error running the script: {e}")