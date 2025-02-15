





def llm_code_executer(python_dependencies, python_code):
    inline_metadata_script = f"""
    /// script
    # requires-python = ">=3.11"
    dependencies = [
    {''.join(f'"{dependency["module"]}",\n' for dependency in python_dependencies)}
    ]
    /// 
    """

    with open("llm_code.py", "w") as f:
        f.write(inline_metadata_script)
        f.write(python_code)

    try:
        output = run(["uv", "run", "llm_code.py"], capture_output=True, text=True, cwd=os.getcwd())
        std_err = output.stderr.split('\n')

        std_out = output.stdout
        exit_code = output.returncode

        for i in range(len(std_err)):
            if std_err[i].lstrip().startswith('File'):
                raise Exception("\n".join(std_err[i:]))

        return {"status": "success", "output": std_out}

    except CalledProcessError as e:
        return {"status": "error", "error": str(e)}

    except Exception as e:
        return {"status": "error", "error": str(e)}
    
primary_prompt = """
You are an automated agent, so generate python code that does the specified task.
Assume uv and python is preinstalled.

If you need to run any uv script then use `uv run {nameofscript} arguments`

Assume that code you generate will be executed inside a docker container.

In order to perform any task if some python package is required to install, provide name of those modules.
"""

def resend_request(task, code, error):
    url = "http://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    update_task = """
    Update the python code

    {code}
    ---
    For below task
    {task}
    ---
    Error encountered while running task
    {error}
    """

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": update_task
            },
            {
                "role": "system",
                "content": """{primary_prompt}"""
            }
        ],
        "response_format": response_format
    }

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }
def task_runner(task: str):
    AI_PROXY_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": task},
            {"role": "system", "content": primary_prompt}
        ],
        "response_format": response_format
    }

    response = requests.post(url=AI_PROXY_URL, headers=HEADERS, json=data)
    r = response.json()
    
    python_dependencies = json.loads(r['choices'][0]['message']['content'])['python_dependencies']
    python_code = json.loads(r['choices'][0]['message']['content'])['python_code']
    
    output = llm_code_executer(python_dependencies, python_code)
    
    limit = 0
    while limit < 2:
        if output == "success":
            return "task completed successfully"
        elif output['error'] != "":
            with open("llm_code.py", "r") as f:
                code = f.read()
            response = resend_request(task, code, output['error'])
            r = response.json()
            
            python_dependencies = json.loads(r['choices'][0]['message']['content'])['python_dependencies']
            python_code = json.loads(r['choices'][0]['message']['content'])['python_code']
            
            output = llm_code_executer(python_dependencies, python_code)
        
        limit += 1

    # print(output)

    return r

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
