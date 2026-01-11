# pylint_tool.py
import subprocess
import json

def run_pylint(filename: str):
    result = subprocess.run(
        ["pylint", filename, "--output-format=json"],
        capture_output=True,
        text=True
    )
    return result.stdout

def parse_pylint_output(output: str):
    try:
        issues = json.loads(output)
        return {"score": 10.0, "issues": issues}
    except json.JSONDecodeError:
        return {"score": 0, "issues": []}
