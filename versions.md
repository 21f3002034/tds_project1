```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#      "fastapi",
#      "uvicorn", 
#      "requests",    
#
#
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


AIPROXY_TOKEN =os.getenv("AIPROXY_TOKEN")
#AIPROXY_TOKEN ="eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDIwMzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KEQjxQbjAIHY8_0l-WpiOL_KrBslnPTFZnexib9N6qc"
tools = [
    {
        "type": "function",
        "function": {
            "name": "script_runner",
            "description": "Install a package and run a script from a url with provided arguments.",
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
        "Content-type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": task
            },
            {
                "role": "system",
                "content": """
                You are an assistant who has to do a variety of tasks
                If your task involves running a script, you can use the script_runner tool.
                If your task involves writing a code, you can use the task_runner tool.
                """
            }
        ],
        "tools": tools,
        "tool_choice": "auto",
    }

    response = requests.post(url=url, headers=headers, json=data)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```


# VERSION TWO A1 COMPLETED
```python
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
import subprocess
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
#AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDIwMzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KEQjxQbjAIHY8_0l-WpiOL_KrBslnPTFZnexib9N6qc"
if not AIPROXY_TOKEN:
    raise ValueError("AIPROXY_TOKEN environment variable is missing!")

def script_runner(script_url, args):
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        arguments=response.json()['choices'][0]['message']['tool_calls'][0]['function']
        args_data = json.loads(arguments["arguments"])

        # Extract script_url and args
        script_url = args_data["script_url"]
        args = args_data["args"]  # Assuming this is already a list

        # Flatten args list
        command = ["uv", "run", script_url] + args + ["--root", "./data"]
        # Run the command
        subprocess.run(command, capture_output=True, text=True)
        return response.json()['choices'][0]['message']['tool_calls'][0]['function']
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

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
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to format."
                },
                "prettier_version": {
                    "type": "string",
                    "description": "The version of Prettier to use."
                }
            },
            "required": ["file_path", "prettier_version"]
        }
    }
}

tools = [A1, A2]
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
                whenever you receive a system directory location, always make it into a relative path, for example adding a . before it would make it relative path, rest is on you to manage, i just want the relative path.
                """
            }
        ],
        "tools": tools,
        "tool_choice": "auto",  # Change to "script_runner" if you want automatic tool execution
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```


# not working
```python
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
import subprocess
import json
from fastapi.responses import StreamingResponse
import mimetypes
from pathlib import Path
from typing import Dict, Any
import base64


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
#AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIxZjMwMDIwMzRAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.KEQjxQbjAIHY8_0l-WpiOL_KrBslnPTFZnexib9N6qc"
if not AIPROXY_TOKEN:
    raise ValueError("AIPROXY_TOKEN environment variable is missing!")

def script_runner(script_url, args):
    try:
        # Flatten args list
        command = ["uv", "run", script_url] + args + ["--root", "./data"]
        # Run the command
        subprocess.run(command, capture_output=True, text=True)
        return {"success": True}
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")

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
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to format."
                },
                "prettier_version": {
                    "type": "string",
                    "description": "The version of Prettier to use."
                }
            },
            "required": ["file_path", "prettier_version"]
        }
    }
}

tools = [A1, A2]

# Initial step to choose task A1,...A10
def query_gpt(user_input: str, tools: list[Dict[str, Any]] = tools) -> Dict[str, Any]:
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
                You are an assistant who has to do a variety of tasks.
                If your task involves running a script, you can use the script_runner tool.
                If your task involves writing code, you can use the task_runner tool.
                whenever you receive a system directory location, always make it into a relative path, for example adding a . before it would make it relative path, rest is on you to manage, i just want the relative path.
                """
            }
        ],
        "tools": tools,
        "tool_choice": "auto",  # Change to "script_runner" if you want automatic tool execution
    }
    
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()
    # arguments=response.json()['choices'][0]['message']['tool_calls'][0]['function']
    # args_data = json.loads(arguments["arguments"])
    # # Extract script_url and args
    # script_url = args_data["script_url"]
    # args = args_data["args"]  # Assuming this is already a list
    # return script_url,args

    
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



@app.get("/run")
async def run(task: str):
    query = query_gpt(task)
    print(query)
    func = eval(query["choices"][0]["message"]["tool_calls"][0]["function"]["name"])
    args = json.loads(query["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"])
    output = func(**args)
    return output

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#A5 completed and working
```python
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
    file_path = os.path.abspath(file_path)  # Convert to absolute path
    
    print(file_path)
    try:
        subprocess.run(f"sudo npm install --global prettier@{prettier_version}", shell=True, check=True)

        # Run Prettier to format the file in-place
        subprocess.run(f"prettier --write {file_path}", shell=True, check=True)

        return {"success": f"File {file_path} formatted using Prettier {prettier_version}"}

    except subprocess.CalledProcessError as e:
        return {"error": f"Prettier formatting failed: {e.stderr} {file_path}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}{file_path}"}

def count_wednesdays(input_file: str, output_file: str):
    wednesday_count = 0
    accepted_formats = ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%B %d, %Y"]
    input_file = os.path.abspath(input_file)  # Convert to absolute path
    output_file = os.path.abspath(output_file)
    with open(f"{input_file}", "r") as file:
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
                   
    with open(output_file, "w") as file:
        file.write(str(wednesday_count))  # Write just the number

    return json.dumps({"output_file": output_file})

def sort_contacts(input_file: str, output_file: str):
    """
    Sort contacts by last name, then first name, and write the result to a JSON file.
    """
    input_file = os.path.abspath(input_file)  # Convert to absolute path
    output_file = os.path.abspath(output_file)

    try:
        with open(input_file, "r") as file:
            contacts = json.load(file)

        if not isinstance(contacts, list):
            return {"error": "Invalid JSON format. Expected a list of contacts."}

        sorted_contacts = sorted(contacts, key=lambda c: (c.get("last_name", "").lower(), c.get("first_name", "").lower()))

        with open(output_file, "w") as file:
            json.dump(sorted_contacts, file, indent=4)

        return {"output_file": output_file}

    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON file."}

    except FileNotFoundError:
        return {"error": f"File not found: {input_file}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def get_recent_log_entries(log_directory: str, output_file: str):
    """
    Extract the first line from the 10 most recent .log files in a directory
    and write them to an output file, most recent first.
    """
    try:
        # Ensure directory exists
        if not os.path.isdir(log_directory):
            return {"error": f"Directory not found: {log_directory}"}
        log_directory=os.path.abspath(log_directory)  # Convert to absolute path
        output_file = os.path.abspath(output_file)
        # Get list of .log files sorted by modification time (most recent first)
        log_files = sorted(
            [os.path.join(log_directory, f) for f in os.listdir(log_directory) if f.endswith(".log")],
            key=lambda f: os.path.getmtime(f),
            reverse=True
        )[:10]  # Take the 10 most recent log files

        log_entries = []

        for log_file in log_files:
            try:
                with open(log_file, "r") as file:
                    first_line = file.readline().strip()  # Read the first line
                    if first_line:
                        log_entries.append(f"{os.path.basename(log_file)}: {first_line}")
            except Exception as e:
                log_entries.append(f"{os.path.basename(log_file)}: [Error reading file] {str(e)}")

        # Write to output file
        with open(output_file, "w") as out_file:
            out_file.write("\n".join(log_entries) + "\n")

        return {"output_file": output_file}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
    
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

A4 = {
    "type": "function",
    "function": {
        "name": "sort_contacts",
        "description": "Sort contacts by last name, then first name, and write the result to a JSON file.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Path to the input JSON file containing contact data."
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output JSON file where sorted contacts will be saved."
                }
            },
            "required": ["input_file", "output_file"]
        }
    }
}

A5 ={
    "type": "function",
    "function": {
        "name": "get_recent_log_entries",
        "description": "Extract the first line from the 10 most recent .log files in /data/logs/ and write them to /data/logs-recent.txt.",
        "parameters": {
            "type": "object",
            "properties": {
                "log_directory": {
                    "type": "string",
                    "description": "Path to the directory containing log files."
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output file where the first lines of the logs will be written."
                }
            },
            "required": ["log_directory", "output_file"]
        }
    }
}

tools = [A1, A2, A3, A4, A5]

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
                like /data/<file> as ./data/<file>
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
```