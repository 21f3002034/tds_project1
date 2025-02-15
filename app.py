# /// script
# requires-python = ">=3.13"
# dependencies = [
#       "flask",
#      "fastapi",
#      "uvicorn", 
#      "requests",
#      "pathlib",
#       "datetime",
#       "openai",
#       "pytesseract",
#       "numpy",
#       "pillow",
#       "sentence_transformers",
#       "scipy",
#      "pandas",
#       "markdown",
#   "SpeechRecognition",
#   "gitpython",
#   "python-multipart",
#   "duckdb",
#   "python-dateutil"
#   
# ]
# ///
import duckdb
import git
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import requests
import os
import subprocess
import json

from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime
import pytesseract
from PIL import Image
import shutil
import duckdb
import markdown
import json
import speech_recognition as sr


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
        # Fetch the script content from the given URL
        
        response = requests.get(script_url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch script from URL")
        
        # Save the content to datagen.py
        datagen_filename = "datagen.py"
        with open(datagen_filename, "w") as f:
            f.write(response.text)

        # Run the script using uv
        command = ["uv", "run", script_url] + args + ["--root", "./data"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        return {"success": True, "output": result.stdout}

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Script execution failed: {e.stderr}")

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching script: {str(e)}")

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
            log_directory="./data/logs"
            # Ensure directory exists
            if not os.path.isdir(log_directory):
                return {"error": f"Directory not found: {log_directory}"}
            # Convert to absolute path
            output_file = "./data/logs-recent.txt"
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
                            with open(output_file, "a") as out_file:
                                print(first_line, file=out_file)                        
                except Exception as e:
                    log_entries.append(f"{os.path.basename(log_file)}: [Error reading file] {str(e)}")

                    

            return {"output_file": output_file}

    except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}

import re

def generate_markdown_index(docs_directory: str, output_file: str):
    """
    Find all Markdown (.md) files in a directory, extract the first H1 title from each file,
    and create an index JSON file mapping filenames to titles.
    """
    docs_directory = os.path.abspath(docs_directory)  # Convert to absolute path
    output_file = os.path.abspath(output_file)
    try:
        # Ensure directory exists
        if not os.path.isdir(docs_directory):
            return {"error": f"Directory not found: {docs_directory}"}

        index_data = {}

        # Iterate over all .md files
        for root, _, files in os.walk(docs_directory):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as md_file:
                            for line in md_file:
                                match = re.match(r"^# (.+)", line.strip())  # Find first H1 title
                                if match:
                                    relative_path = os.path.relpath(file_path, docs_directory)  # Remove full path prefix
                                    index_data[relative_path] = match.group(1)  # Store filename -> title
                                    break  # Stop after first H1
                    except Exception as e:
                        index_data[file] = f"[Error reading file] {str(e)}"

        # Write index to JSON file
        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(index_data, json_file, indent=4)

        return {"output_file": output_file}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
    
    # FOR CREDIT CARD
def pass_number(number_str: str) -> bool:
    """
    Returns True if 'number_str' (containing only digits) satisfies the Luhn check.
    """
    if not number_str.isdigit():
        return False
    
    digits = [int(d) for d in number_str]
    # Double every second digit from the right
    for i in range(len(digits) - 2, -1, -2):
        doubled = digits[i] * 2
        # If doubling is >= 10, subtract 9
        if doubled > 9:
            doubled -= 9
        digits[i] = doubled
    
    return sum(digits) % 10 == 0
def extract_credit_card_number(input_file: str, output_file: str):
    """
    1. Reads /data/credit-card.png
    2. Extracts a 16-digit number via Tesseract OCR
    3. Applies Luhn check. If it fails and the first digit is '9',
       try replacing it with '3' and check again.
    4. Writes the final 16-digit number to /data/credit-card.txt
    """
    input_file = os.path.abspath(input_file)  # Convert to absolute path
    output_file = os.path.abspath(output_file)
    # input_file = os.path.join(os.getcwd(), "data", "credit_card.png")
    # output_file = os.path.join(os.getcwd(), "data", "credit-card.txt")

    try:
        # 1. Load the image
        img = Image.open(input_file)

        # 2. Configure Tesseract for digits only
        custom_config = r"--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789"
        extracted_text = pytesseract.image_to_string(img, config=custom_config)

        # 3. Extract lines, look for a line with exactly 16 digits
        lines = extracted_text.splitlines()
        recognized_16 = None
        for line in lines:
            digits = re.sub(r"\D", "", line)  # keep only digits
            if len(digits) == 16:
                recognized_16 = digits
                break

        if not recognized_16:
            return {
                "error": "No line with exactly 16 digits found.",
                "ocr_output": extracted_text
            }

        # 4. Check Luhn
        if pass_number(recognized_16):
            final_number = recognized_16
        else:
            # If first digit is '9', try flipping it to '3'
            if recognized_16[0] == '9':
                possible_fix = '3' + recognized_16[1:]
                if pass_number(possible_fix):
                    final_number = possible_fix
                else:
                    return {
                        "error": "Luhn check failed, flipping '9'->'3' also failed.",
                        "recognized_number": recognized_16
                    }
            else:
                return {
                    "error": "Luhn check failed and no known fix.",
                    "recognized_number": recognized_16
                }

        # 5. Write final_number to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_number + "\n")

        return {"written_file": output_file, "card_number": final_number}

    except Exception as e:
        return {"error": str(e)}
    

import itertools
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cosine

def find_most_similar_comments(input_file: str, output_file: str):
    """
    Find the most similar pair of comments using embeddings and write them to a file.
    """
    input_file = os.path.abspath(input_file)  # Convert to absolute path
    output_file = os.path.abspath(output_file)
    try:
        # Ensure input file exists
        if not os.path.isfile(input_file):
            return {"error": f"File not found: {input_file}"}

        # Load comments
        with open(input_file, "r", encoding="utf-8") as file:
            comments = [line.strip() for line in file if line.strip()]

        if len(comments) < 2:
            return {"error": "Insufficient comments to compare (need at least two)."}

        # Load pre-trained embedding model
        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Compute embeddings
        embeddings = model.encode(comments)

        # Find the most similar pair
        min_distance = float("inf")
        most_similar_pair = None

        for c1, c2 in itertools.combinations(range(len(comments)), 2):
            distance = cosine(embeddings[c1], embeddings[c2])
            if distance < min_distance:
                min_distance = distance
                most_similar_pair = (comments[c1], comments[c2])

        if not most_similar_pair:
            return {"error": "Failed to find similar comments."}

        # Write the most similar pair to output file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(most_similar_pair[0] + "\n")
            file.write(most_similar_pair[1] + "\n")

        return {"output_file": output_file}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

import os


import os
import duckdb

def calculate_gold_ticket_sales(db_file: str, output_file: str):
    """
    Calculate total sales for 'Gold' ticket type and write the result to a file using DuckDB.
    """
    db_file = os.path.abspath(db_file)  # Convert to absolute path
    output_file = os.path.abspath(output_file)

    try:
        # Ensure database file exists
        if not os.path.isfile(db_file):
            return {"error": f"Database file not found: {db_file}"}

        # Connect to DuckDB database
        conn = duckdb.connect(db_file)

        # Query to calculate total sales for 'Gold' tickets
        query = "SELECT SUM(units * price) FROM tickets WHERE type = 'Gold';"
        result = conn.execute(query).fetchone()[0]

        # Close database connection
        conn.close()

        # If no sales found, set result to 0
        total_sales = result if result is not None else 0

        # Write the total sales to output file
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(str(total_sales) + "\n")

        return {"output_file": output_file}

    except duckdb.Error as e:
        return {"error": f"DuckDB error: {str(e)}"}

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
        "description": "Extract the first line from the 10 most recent .log files in ./data/logs/ and write them to ./data/logs-recent.txt.",
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

A6 = {
    "type": "function",
    "function": {
        "name": "generate_markdown_index",
        "description": "Find all Markdown (.md) files in /data/docs/, extract the first H1 title from each file, and create an index JSON file mapping filenames to titles.",
        "parameters": {
            "type": "object",
            "properties": {
                "docs_directory": {
                    "type": "string",
                    "description": "Path to the directory containing Markdown (.md) files. Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output JSON file where the index will be saved.Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                }
            },
            "required": ["docs_directory", "output_file"]
        }
    }
}

A7 = {
    "type": "function",
    "function": {
        "name": "extract_email_sender",
        "description": "Extract the sender's email address from an email message and save it to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Path to the input text file containing the email message.Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output text file where the sender's email address will be saved.Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                }
            },
            "required": ["input_file", "output_file"]
        }
    }
}

A8 = {
    "type": "function",
    "function": {
        "name": "extract_credit_card_number",
        "description": "Extract the credit card number from an image and save it to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Path to the input image file containing the credit card number.Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output text file where the extracted credit card number will be saved.Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                }
            },
            "required": ["input_file", "output_file"]
        }
    }
}

A9 ={
    "type": "function",
    "function": {
        "name": "find_most_similar_comments",
        "description": "Find the most similar pair of comments using embeddings and write them to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "input_file": {
                    "type": "string",
                    "description": "Path to the input text file containing comments, one per line."
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output text file where the most similar pair of comments will be saved."
                }
            },
            "required": ["input_file", "output_file"]
        }
    }
}

A10 = {
    "type": "function",
    "function": {
        "name": "calculate_gold_ticket_sales",
        "description": "Calculate total sales for 'Gold' ticket type and write the result to a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "db_file": {
                    "type": "string",
                    "description": "Path to the SQLite database file containing the ticket sales data."
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output text file where the total sales amount for 'Gold' tickets will be saved."
                }
            },
            "required": ["db_file", "output_file"]
        }
    }
}

B3 = {
    "type": "function",
    "function": {
        "name": "fetch_and_save_api_data",
        "description": "Fetch data from an API and save it to a file inside /data. Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  ",
        "parameters": {
            "type": "object",
            "properties": {
                "api_url": {
                    "type": "string",
                    "description": "The API endpoint URL to fetch data from."
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output file inside /data where the API response will be saved."
                }
            },
            "required": ["api_url", "output_file"]
        }
    }
}

B4 = {
    "type": "function",
    "function": {
        "name": "clone_and_commit_git_repo",
        "description": "Clone a git repository and make a commit.",
        "parameters": {
            "type": "object",
            "properties": {
                "repo_url": {
                    "type": "string",
                    "description": "The Git repository URL to clone."
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message for the new commit."
                }
            },
            "required": ["repo_url", "commit_message"]
        }
    }
}

B5 = {
    "type": "function",
    "function": {
        "name": "execute_sql_query",
        "description": "Run a SQL query on a SQLite or DuckDB database.",
        "parameters": {
            "type": "object",
            "properties": {
                "db_path": {
                    "type": "string",
                    "description": "Path to the SQLite or DuckDB database inside ./data. Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                },
                "query": {
                    "type": "string",
                    "description": "SQL query to execute."
                }
            },
            "required": ["db_path", "query"]
        }
    }
}

B6 = {
    "type": "function",
    "function": {
        "name": "scrape_website_data",
        "description": "Extract data from a website. ",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the website to scrape. Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output file inside ./data where scraped data will be saved. Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                }
            },
            "required": ["url", "output_file"]
        }
    }
}

B7 = {
    "type": "function",
    "function": {
        "name": "compress_or_resize_image",
        "description": "Compress or resize an image inside ./data. Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  ",
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image inside /data."
                },
                "output_path": {
                    "type": "string",
                    "description": "Path to save the resized or compressed image inside /data."
                },
                "width": {
                    "type": "integer",
                    "description": "Optional width for resizing."
                },
                "height": {
                    "type": "integer",
                    "description": "Optional height for resizing."
                }
            },
            "required": ["image_path", "output_path"]
        }
    }
}

B8 = {
    "type": "function",
    "function": {
        "name": "transcribe_audio",
        "description": "Transcribe audio from an MP3 file inside ./data. Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  ",
        "parameters": {
            "type": "object",
            "properties": {
                "audio_path": {
                    "type": "string",
                    "description": "Path to the MP3 file inside ./data."
                },
                "output_file": {
                    "type": "string",
                    "description": "Path to the output text file inside /data where the transcription will be saved. Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  "
                }
            },
            "required": ["audio_path", "output_file"]
        }
    }
}



tools = [A1, A2, A3, A4, A5, A6, A7, A8, A9, A10, B3, B4, B5, B6, B7, B8]

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
        Use the following functions for specific tasks:  
        
        - Use 'script_runner' for running scripts.  
        - Use 'format_file' for formatting files.  
        - Use 'scrape_website_data' for scraping website data.  
        - Use 'process_csv' for handling CSV file operations.  
        - Use 'generate_report' for creating reports.  
        - Use 'parse_json' for parsing JSON data.  
        - Use 'extract_text' for extracting text from documents.  
        - Use 'translate_text' for translating text between languages.  
        - Use 'analyze_sentiment' for performing sentiment analysis.  
        - Use 'compress_file' for compressing files.  
        - Use 'resize_image' for resizing images.  
        - Use 'convert_audio' for converting audio formats.  
        - Use 'fetch_api_data' for fetching data from APIs.  
        - Use 'execute_sql' for running SQL queries.  
        - Use 'send_email' for sending emails.  
        - Use 'log_activity' for logging system activities.  
        - Use 'validate_input' for input validation.  
        - Use 'hash_data' for hashing sensitive data.  
        
        Always return relative paths for system directory locations.         Example: Use './data/<file>' instead of '/data/<file>'.  
    
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

def scrape_website(url):
    response = requests.get(url)
    return response.text if response.status_code == 200 else "Failed to scrape"


data_dir = "/data"
def ensure_safe_path(path):
    if not os.path.abspath(path).startswith(data_dir):
        raise HTTPException(status_code=403, detail="Access outside /data is not allowed")

@app.post("/fetch_api")
def fetch_api(url: str, filename: str):
    ensure_safe_path(os.path.join(data_dir, filename))
    response = requests.get(url)
    with open(os.path.join(data_dir, filename), "wb") as f:
        f.write(response.content)
    return {"message": "Data saved"}

@app.post("/clone_repo")
def clone_repo(repo_url: str, branch: str = "main"):
    repo_path = os.path.join(data_dir, "repo")
    ensure_safe_path(repo_path)
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
    git.Repo.clone_from(repo_url, repo_path, branch=branch)
    return {"message": "Repository cloned"}

@app.post("/commit_repo")
def commit_repo(filename: str, content: str, message: str):
    repo_path = os.path.join(data_dir, "repo")
    ensure_safe_path(repo_path)
    with open(os.path.join(repo_path, filename), "w") as f:
        f.write(content)
    repo = git.Repo(repo_path)
    repo.git.add(filename)
    repo.index.commit(message)
    repo.remote().push()
    return {"message": "Commit pushed"}

@app.post("/run_sql")
def run_sql(db_type: str, db_path: str, query: str):
    ensure_safe_path(db_path)
    
    if db_type == "sqlite":
        # Change SQLite to DuckDB
        db_type = "duckdb"

    conn = duckdb.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.commit()
    conn.close()
    return {"result": result}

@app.post("/scrape")
def scrape_website(url: str):
    response = requests.get(url)
    return {"content": response.text}

@app.post("/compress_image")
def compress_image(file: UploadFile, quality: int = 50):
    img = Image.open(file.file)
    output_path = os.path.join(data_dir, file.filename)
    ensure_safe_path(output_path)
    img.save(output_path, "JPEG", quality=quality)
    return {"message": "Image compressed"}

@app.post("/transcribe")
def transcribe_audio(file: UploadFile):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file.file) as source:
        audio = recognizer.record(source)
    text = recognizer.recognize_google(audio)
    return {"transcription": text}

@app.post("/convert_md")
def convert_md(content: str):
    html = markdown.markdown(content)
    return {"html": html}
@app.post("/filter_csv")
def filter_csv(file: UploadFile, column: str, value: str):
    import pandas as pd
    df = pd.read_csv(file.file)
    filtered_df = df[df[column] == value]
    return json.loads(filtered_df.to_json(orient="records"))


# Run server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)