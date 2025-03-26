from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import pytesseract
from PIL import Image
from ollama import generate
import io
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins, change this for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

def generate_robot_tests(image_file, model_name, requirements_text):
    try:
        image = Image.open(image_file)
        extracted_text = pytesseract.image_to_string(image)
    except Exception as e:
        return {"error": f"Error processing image: {e}"}

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
        return {"test_cases": test_cases}
    except Exception as e:
        return {"error": f"Error generating test cases: {e}"}


@app.post("/generate_tests/")
async def generate_tests(image: UploadFile = File(...), model_name: str = Form(...), requirements_text: str = Form(None)):
    try:
        image_file = io.BytesIO(await image.read())
        result = generate_robot_tests(image_file, model_name, requirements_text)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)})
