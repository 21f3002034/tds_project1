# /// script
# requires-python = ">=3.13"
# dependencies = [
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
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

app = FastAPI()

# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Load API Token
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    raise ValueError("AIPROXY_TOKEN environment variable is missing!")

# Function to run external scripts
def script_runner(script_url, args):
    try:
        command = ["uv", "run", script_url] + args + ["--root", "./data"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"success": True, "output": result.stdout}
    
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Script execution failed: {e.stderr}")

def format_file(file_path: str, prettier_version: str):
    """
    Format a file using a specified version of Prettier.
    """
    print(file_path)
    try:
        subprocess.run(f"sudo npm install --global prettier@{prettier_version}", shell=True, check=True)

        # Run Prettier to format the file in-place
        subprocess.run(f"prettier --write .{file_path}", shell=True, check=True)

        return {"success": f"File {file_path} formatted using Prettier {prettier_version}"}

    except subprocess.CalledProcessError as e:
        return {"error": f"Prettier formatting failed: {e.stderr} {file_path}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}{file_path}"}

def count_wednesdays(input_file: str, output_file: str):
    wednesday_count = 0
    accepted_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%B %d, %Y"]

    with open(f".{input_file}", "r") as file:
        for line in file:
            date_str = line.strip()
            for fmt in accepted_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    if date_obj.weekday() == 2:  # Wednesday
                        wednesday_count += 1
                    break  # Stop checking formats if parsing succeeds
                except ValueError:
                    continue  # Try next format
    output_file=f".{output_file}"                
    with open(output_file, "w") as file:
        file.write(str(wednesday_count))  # Write just the number

    return json.dumps({"output_file": output_file})
    
# Tools for LLM interaction
A1=    {
        "type": "function",
        "function": {
            "name": "script_runner",
            "description": "Install a package and run a script from a URL with provided arguments.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_url": {
                        "type": "string",
                        "description": "The URL of the script to run."
                    },
                    "args": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "List of arguments to pass to the script"
                    }
                },
                "required": ["script_url", "args"]
            }
        }
    }

A2 = {
    "type": "function",
    "function": {
        "name": "format_file",
        "description": "Format a file using a specified version of Prettier.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file to format."},
                "prettier_version": {"type": "string", "description": "Version of Prettier to use."}
            },
            "required": ["file_path", "prettier_version"]
        }
    }
}

A3 = {
    "type": "function",
    "function": {
        "name": "count_wednesdays",
        "description": "Count the number of Wednesdays in a file containing dates and save the count to another file.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_file": {"type": "string", "description": "Path to the input file containing dates."},
                "output_file": {"type": "string", "description": "Path to the output file to save the count of Wednesdays."}
            },
            "required": ["input_file", "output_file"]
        }
    }
}


tools = [A1, A2, A3]

# Function to query GPT API
def query_gpt(user_input: str) -> Dict[str, Any]:
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": user_input},
            {
                "role": "system",
                "content": """
                You are an assistant capable of executing various tasks.
                - Use 'script_runner' for running scripts.
                - Use 'format_file' for formatting files.
                Always return relative paths for system directory locations.
                """
            }
        ],
        "tools": tools,
        "tool_choice": "auto",
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"GPT query failed: {str(e)}")

# API Endpoints
@app.get("/")
def home():
    return {"message": "LLM Agent API Running"}

@app.get("/read")
def read_file(path: str = Query(..., description="Path to the file")):
    # Normalize path (remove leading /)
    normalized_path = path.lstrip("/")

    # Ensure path is inside the project directory
    base_path = Path(__file__).parent  # Gets the directory where app.py is located
    file_path = base_path / normalized_path  # Resolves relative to project

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        with file_path.open("r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@app.post("/run")
async def run(task: str):
    query = query_gpt(task)
    
    try:
        tool_call = query["choices"][0]["message"]["tool_calls"][0]
        func_name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])

        if func_name in globals():
            return globals()[func_name](**args)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown function: {func_name}")
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise HTTPException(status_code=500, detail=f"Error processing GPT response: {str(e)}")

# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
