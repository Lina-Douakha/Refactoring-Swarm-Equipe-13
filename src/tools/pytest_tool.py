# pytest_tool.py
import subprocess
import json

def run_pytest(test_dir: str):
    result = subprocess.run(
        ["pytest", test_dir, "--json-report", "--tb=short"],
        capture_output=True,
        text=True
    )
    return result.stdout

def parse_test_results(output: str):
    try:
        with open(".report.json") as f:
            report = json.load(f)
        passed = sum(1 for t in report["tests"] if t["outcome"] == "passed")
        failed = sum(1 for t in report["tests"] if t["outcome"] == "failed")
        return {"success": failed == 0, "passed": passed, "failed": failed, "errors":[t["nodeid"] for t in report["tests"] if t["outcome"]=="failed"]}
    except FileNotFoundError:
        return {"success": False, "passed":0, "failed":0, "errors":["report not found"]}
