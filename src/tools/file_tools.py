import os
import sys
try:
    from ..utils.sandbox_guard import get_absolute_safe_path
except (ImportError, ValueError):
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    try:
        from utils.sandbox_guard import get_absolute_safe_path
    except ImportError:
        raise ImportError("Cannot import get_absolute_safe_path from utils.sandbox_guard. Check your project structure and run mode.")

def read_file_safe(filename: str) -> str:
    path = get_absolute_safe_path(filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file_safe(filename: str, content: str):
    path = get_absolute_safe_path(filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def list_python_files(directory: str):
    path = get_absolute_safe_path(directory)
    return [f for f in os.listdir(path) if f.endswith(".py")]

def get_file_content(filename: str) -> str:
    return read_file_safe(filename)
