# /// script
# requires-python = ">=3.13"
# dependencies = [
#      "fastapi",
#      "uvicorn", 
#      "requests"
# ]
# ///

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDIwMzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KEQjxQbjAIHY8_0l-WpiOL_KrBslnPTFZnexib9N6qc"
if not AIPROXY_TOKEN:
    raise ValueError("AIPROXY_TOKEN environment variable is missing!")

tools = [
    {
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
]

@app.get("/")
def home():
    return {"message": "Working FROM DOCKER"}

@app.get("/read")
def read_file(path: str = Query(..., description="Path to the file")):
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File doesn't exist")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@app.post("/run")
def task_runner(task: str):
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": task},
            {
                "role": "system",
                "content": """
                You are an assistant who has to do a variety of tasks.
                If your task involves running a script, you can use the script_runner tool.
                If your task involves writing code, you can use the task_runner tool.
                """
            }
        ],
        "tools": tools,
        "tool_choice": "auto",  # Change to "script_runner" if you want automatic tool execution
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['tool_calls'][0]['function']
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
