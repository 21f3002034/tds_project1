# /// script
# requires-python = ">=3.13"
# dependencies = [
#       "flask",
#      "fastapi",
#      "uvicorn", 
#      "requests",
#      "pathlib",
#       "datetime"
# ]
# ///



from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import os
import subprocess
import json
import random
import string
from pathlib import Path

def get_ai_proxy_token():
    token = os.getenv("AIPROXY_TOKEN")
    if not token:
        raise RuntimeError("AIPROXY_TOKEN environment variable is not set")
    return token

app = FastAPI()
AIPROXY_TOKEN = get_ai_proxy_token()

# Allow CORS for frontend integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


    
@app.post("/run")
def task_runner(task: str = Query(..., description="Task description in plain English")):
    """Receives a task description, generates a Python script using GPT-4o, and executes it."""
    # AI Proxy Endpoint
    AI_PROXY_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    PRIMARY_PROMPT = """
    Generate a Python program that accomplishes the given task. The program should follow best practices and ensure correctness.
    Provide the output as json containing only two fields: 'python_code' with the Python script as a string, and 'python_dependencies' as a list of required dependencies.
    """
    # Prepare the request to the LLM
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": task},
            {"role": "system", "content": PRIMARY_PROMPT}
        ],
        "response_format": response_format
    }

    try:
        response = requests.post(url=AI_PROXY_URL, headers=HEADERS, json=data)
        return response.json()
        response.raise_for_status()
        response_data = response.json()
        content = json.loads(response_data['choices'][0]['message']['content'])
        python_code = content['python_code']
        python_dependencies = content.get('python_dependencies', [])
    except (KeyError, json.JSONDecodeError, requests.RequestException) as e:
        raise HTTPException(status_code=500, detail=f"Error fetching AI-generated code: {str(e)}")
    
    # Generate a random filename for the script
    script_name = f"task_{''.join(random.choices(string.ascii_lowercase, k=8))}.py"
    script_path = Path(script_name)
    
    # Write the generated script to a file
    with open(script_path, "w") as script_file:
        script_file.write(python_code)
    
    # Ensure dependencies are installed
    if python_dependencies:
        dependencies = " ".join(python_dependencies)
        subprocess.run(["pip", "install", *python_dependencies], check=True)
    
    # Execute the script using Python
    try:
        result = subprocess.run(["python", script_name], capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        output = f"Error executing script: {e.stderr}"
    finally:
        os.remove(script_path)
    
    return {"task": task, "output": output}  

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
