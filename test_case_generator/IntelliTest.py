import streamlit as st
import pytesseract
from PIL import Image
from ollama import generate


def generate_robot_tests(image_path, model_name, requirements_text):
    try:
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        st.write("Extracted UI elements:")
        st.text(extracted_text)
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

    default_requirements = '''Include:
1. Valid login test
2. Invalid login test
3. Empty field validation
Use this format:
*** Test Cases ***
[Test Name]
    [Action]    [Locator]    [Value]'''

    requirements = requirements_text if requirements_text else default_requirements
    prompt = f"""Generate Robot Framework test cases for this UI:
{extracted_text}

Requirements:
{requirements}"""

    try:
        response = generate(model=model_name, prompt=prompt, options={'temperature': 0.7})
        test_cases = response['response']
        return test_cases
    except Exception as e:
        st.error(f"Error generating test cases: {e}")
        return None


st.title("DI-Sculpt QA Assistant")

uploaded_image = st.file_uploader("Upload a UI screenshot", type=['png', 'jpg', 'jpeg'])
requirements_file = st.file_uploader("Upload test requirements (optional)", type=['txt'])
model_name = st.text_input("Ollama Model Name", value="deepseek-coder")

if st.button("Generate Test Cases"):
    if uploaded_image:
        requirements_text = None
        if requirements_file:
            requirements_text = requirements_file.read().decode("utf-8")

        test_cases = generate_robot_tests(uploaded_image, model_name, requirements_text)

        if test_cases:
            st.subheader("Generated Robot Framework Test Cases:")
            st.code(test_cases, language="robotframework")
    else:
        st.warning("Please upload a UI screenshot to proceed.")
