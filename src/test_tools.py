import os
import sys
try:
    from utils.sandbox_guard import get_absolute_safe_path
    from tools.file_tools import list_python_files, read_file_safe, write_file_safe
    from tools.pylint_tool import run_pylint, parse_pylint_output
    from tools.pytest_tool import run_pytest, parse_test_results
except ImportError:
    src_dir = os.path.abspath(os.path.dirname(__file__))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    try:
        from utils.sandbox_guard import get_absolute_safe_path
        from tools.file_tools import list_python_files, read_file_safe, write_file_safe
        from tools.pylint_tool import run_pylint, parse_pylint_output
        from tools.pytest_tool import run_pytest, parse_test_results
    except ImportError:
        raise ImportError("Impossible d'importer les modules nécessaires. Vérifiez la structure du projet et le mode d'exécution.")


# chemin absolu vers sandbox
sandbox_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sandbox"))
print("=== Liste des fichiers Python dans sandbox ===")

py_files = list_python_files(sandbox_path)
for f in py_files:
    content = read_file_safe(os.path.join(sandbox_path, f))
    print(content)



print("\n=== Contenu du premier fichier ===")
if py_files:
    content = read_file_safe(os.path.join(sandbox_path, py_files[0]))
    print(content)

print("\n=== Test Pylint sur le premier fichier ===")
if py_files:
    pylint_output = run_pylint(os.path.join(sandbox_path, py_files[0]))
    pylint_parsed = parse_pylint_output(pylint_output)
    print(pylint_parsed)

print("\n=== Test Pytest sur sandbox ===")
pytest_output = run_pytest(sandbox_path)
print("\n--- Sortie brute Pytest ---")
print(pytest_output)
pytest_parsed = parse_test_results(pytest_output)
print("\n--- Résumé analyse rapport ---")
print(pytest_parsed)
