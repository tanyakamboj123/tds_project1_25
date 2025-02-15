#/// Scirpt
# requires-python = ">=3.13"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "requests",
# ]
#///

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import requests
import os
import json
from subprocess import run

app = FastAPI()

response_format = {
    "type": "json",
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

@app.get("/")
def home():
    return {"welcome to the task runner"}
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

    return r

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)