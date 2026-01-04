import os

SANDBOX_DIR = os.path.abspath("sandbox")

def is_path_safe(path: str) -> bool:
    return os.path.abspath(path).startswith(SANDBOX_DIR)

def get_absolute_safe_path(path: str) -> str:
    if not is_path_safe(path):
        raise PermissionError(f"Access denied: {path}")
    return os.path.abspath(path)