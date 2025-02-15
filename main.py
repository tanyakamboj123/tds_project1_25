# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "rich",
#   "fastapi",
#   "uvicorn",
# ]
# ///

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import requests
import os
import json
from subprocess import run

app = FastAPI()

response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "taks_runner",
        "schema": {
            "type": "object",
            "required": ["python_dependencies","python_code"],
            "properties": {
                "python_code": {
                    "type": "string",
                    "description": "Python code to perform the task"
                },
                "python_dependencies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "module": {
                                "type": "string",
                                "description": "Name of the python module"
                            }
                        },
                        "required": ["module"],
                        "additionalProperties": False
                    }
            }
        }
    }
}
}

primary_prompt = """
                You are an automated agent, so generate python code that does the specified task.
                Assume that uv and python are pre-installed.
                Assume that code you generate will be executed inside a docker container.
                Inorder to perform any task if some python package is required to install, provide name of those modules. 
                If additional Python packages are required, **list them explicitly**.
                Do not include built-in modules** like `json`, `datetime`, `os`, etc.
                Write a python code for every task and execute the result.
                For one task you have to generate data files with argument provided. Download `datagen.py` from GitHub, execute it with the given email, and save the output files in a `data/` directory.
## **TASK INSTRUCTIONS**
You will receive a task description. Follow these rules:
1. **Identify the type of task.** The task may involve:
   - Running a script
   - Formatting a file
   - Processing text or data
   - Querying a database
   - Extracting or transforming information
   - Fetching data from an API
   - Manipulating files (sorting, extracting, counting, etc.)
2. **Generate the required Python code and commands.** Ensure:
   - Any required **external** Python libraries are included.
   - The code runs correctly in a **Docker environment**.
   - The **data directory (`./data/`) exists** before reading/writing files.

3. **Handle file paths correctly.**
   - **Always use `./data/` instead of `/data/`**.
   - **Ensure `./data/` exists before writing** (use `os.makedirs('./data/', exist_ok=True)`) in Python.
   - **Read files using relative paths** (e.g., `open('./data/contacts.json', 'r')`).
   

4. **Return the response as structured JSON.** The response must contain:
   - `"python_code"`: The Python code to execute.
   - `"python_dependencies"`: A list of external libraries **(excluding built-in modules)**.
   - `"shell_commands"`: Any additional shell commands to execute.
   - `"output_files"`: Expected output file names.
   
** more tasks to Identify the type of task.** It may involve:
   - Fetching data from an API and saving it 
   - Cloning a Git repo and making a commit
   - Running a SQL query on a SQLite or DuckDB database
   - Extracting data from a website (scraping) 
   - Compressing or resizing an image 
   - Transcribing audio from an MP3 file 
   - Converting Markdown to HTML
   - Writing an API endpoint to filter a CSV file and return JSON
   
-Or you may be given tasks to sort and handle the data carefully. Sometimes data are not same in all lines so first format the data according to the tasks and then provide answer.
And do give the text result on the console also . and try to handle all tasks given to you a as you are an intelligent agent.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {AIPROXY_TOKEN}"
}
    
    
    
   
@app.post("/run")
def task_runnner(task: str):
    url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
    data = {
        "model": "gpt-4o-mini", 
         "messages": [
             {
              "role": "user", 
              "content": task
              },
              {
                "role": "system",
                "content": f"""{primary_prompt}"""
            }
         ],
         "response_format": response_format
    }

    response = requests.post(url=url, headers=headers, json=data)
    r = response.json()
   
    python_dependencies= json.loads(r['choices'][0]['message']['content'])['python_dependencies']
    inline_metadata_script= f"""# /// script
# requires-python = ">=3.11"
# dependencies = [
{''.join(f"#  \"{dependency['module']}\",\n" for dependency in python_dependencies)}# ]
# ///

"""
   
    code= json.loads(r['choices'][0]['message']['content'])['python_code']
    with open('to_code.py',"w") as f:
        f.write(inline_metadata_script)
        f.write(code)
        
    output= run(["uv", "run","to_code.py"], capture_output= True, text=True, cwd=os.getcwd())
    print(output)
    return r

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)