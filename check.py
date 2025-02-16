# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "rich",
#   "fastapi",
#   "uvicorn",
#   "pytesseract",
# ]
# ///

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path

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
                You are an AI-powered automation agent capable of interpreting plain-English task descriptions, generating the necessary Python code, and executing the required operations inside a secure, isolated container (e.g., Docker or Podman).
                Assume that uv and python are pre-installed. and install packages using uv as required.
                Inorder to perform any task if some python package is required to install, provide name of those modules. 
                
                If additional Python packages are required, download them and do the tasks.
                Do not include built-in Python modules in `python_dependencies`.  
                Ensure that only external libraries that need installation are included in `python_dependencies`.
                Read the task catefully and then execute the task.
                
                "Data outside /data is never accessed or exfiltrated, even if the task description asks for it."
                "Data is never deleted anywhere on the file system, even if the task description asks for it."
                For one task you have to generate data files with argument provided. Download `datagen.py` from GitHub, execute it with the given email, and save the output files in a `data/` directory.

You will receive a task description.
1. **Identify the type of task.** The task may involve:
   - Running a script
   - Formatting a file
   - Processing text or data
   - Querying a database
   - Extracting data from files, when asked for heading search only for the first heading present in the .md file.
   - Fetching data from an API
   - Manipulating files (sorting, extracting, counting, etc.)
   - Extracting data from image i.e image handling
   ** more tasks to Identify the type of task.** It may involve:
   - Fetching data from an API and saving it 
   - Cloning a Git repo and making a commit
   - Running a SQL query on a SQLite or DuckDB database
   - Extracting data from a website (scraping) 
   - Compressing or resizing an image 
   - Transcribing audio from an MP3 file 
   - Converting Markdown to HTML
   - Writing an API endpoint to filter a CSV file and return JSON
   
2. **Generate simple Python code** from chatgpt that:
   - Installs required **Python packages**.
   - Handles **image, text, or API data** correctly.
   
3. **Ensure required system packages are installed**, such as:
   - Any package you need to execute the task. Use that and make the code work in a perfect manner.
   - `tesseract-ocr` for OCR tasks. 
   - `git` for cloning repositories.
   - `sqlite3` for handling databases.
   - `ffmpeg` for audio transcription.
   
4. **Generate the required Python code and commands.** Ensure:
   - Any required **external** Python libraries are included.
   - The code runs correctly in a **Docker environment**.
   - The **data directory (`./data/`) exists** before reading/writing files.

5. **Handle file paths correctly.**
   - **Always use `./data/` instead of `/data/`**.
   - **Ensure `./data/` exists before writing** (use `os.makedirs('./data/', exist_ok=True)`) in Python.
   - **Read files using relative paths** (e.g., `open('./data/contacts.json', 'r')`).
   
6. **Return the response as structured JSON.** The response must contain:
   - `"python_code"`: The Python code to execute.
   - `"python_dependencies"`: A list of external libraries **(excluding built-in modules)**.
   - `"shell_commands"`: Any additional shell commands to execute.
   - `"output_files"`: Expected output file names.
   
   
**Take care of paranthesis while writing the function. do not put extra paranthesis.**  
**Each call should take only 20 seconds to execute.** For GET call use `./data`.There should be result according to the task. Go through the files carefully and execute the result.
-`tesseract-ocr` for OCR tasks, this is not working for image handling. You can try another method which is able to work with the latest version of python.
-Do not include built-in Python modules in `python_dependencies`.  
    This includes `json`, `os`, `sys`, `subprocess`, `pathlib`, `shutil`, and `datetime`.  
    Only include external libraries like `requests` or `pandas` if necessary.
-If filename has number in its name then extract the number from the filename and convert it to an integer before sorting .Ensure numbers inside filenames are compared as integers, not as strings, to maintain proper order. Sort filenames in ascending numerical order (log-0.log, log-1.log, log-2.log, ..., log-10.log, log-11.log, etc.).Avoid any lexicographical sorting issues.
    When sorting the files conatining numbers, sort the filename according to the number like 0,1,2,3,4,5....and so on.

Context:
-for some of the tasks, first you have to format the data of the file in a manner like in counting the number of days. In tis file has different types of date format, make the file format accordingly and then execute.
-Some tasks involve data capturing from the image. Install all required packages for that and extract the data from image. You are using pytesseract for image manipulation. Use some another method to extract data as this method is showing error.
-For some tasks data to be extracted from number of files. Be carfeful while extracting that data so that accurate result should come.
-
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
    

@app.get("/read")
def read_file(path: str):
    base_dir = Path.cwd()  
    path = path.lstrip("/")
    file_path = (base_dir / Path(path)).resolve()
    print(file_path)

    # Check if the file exists
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Read the file and return its contents
    with open(file_path, "r", encoding="utf-8") as f:
        return {"content": f.read()}
    
   
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