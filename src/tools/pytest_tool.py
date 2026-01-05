import subprocess
import json
import os
import sys

def run_pytest(test_dir: str) -> dict:
    """
    Exécute pytest sur un dossier et retourne les résultats.
    Accepte TOUS les fichiers .py, même sans fonctions test_*
    
    Args:
        test_dir: Dossier contenant les fichiers Python
        
    Returns:
        dict: Résultats des tests
    """
    
    report_path = os.path.join(test_dir, ".report.json")
    
    
    result = subprocess.run(
        [
            "pytest", 
            test_dir,
            "--python_files=*.py",      
            "--python_classes=*",        
            "--python_functions=*",      
            "--json-report",
            f"--json-report-file={report_path}",
            "--tb=short",
            "-v",
            "--ignore-glob=__pycache__/*"
        ],
        capture_output=True,
        text=True
    )
    
    
    return parse_test_results(report_path, result.stdout, result.stderr, test_dir)

def parse_test_results(report_path: str, stdout: str, stderr: str, test_dir: str) -> dict:
    """
    Parse les résultats de pytest.
    Si aucun test trouvé, considère que le code s'exécute sans erreur = SUCCESS
    
    Args:
        report_path: Chemin du fichier de rapport JSON
        stdout: Sortie standard de pytest
        stderr: Sortie d'erreur de pytest
        test_dir: Dossier testé
        
    Returns:
        dict: Résultats structurés
    """
    try:
        
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            
            tests = report.get("tests", [])
            passed = sum(1 for t in tests if t.get("outcome") == "passed")
            failed = sum(1 for t in tests if t.get("outcome") == "failed")
            
            
            if tests:
                errors = []
                for test in tests:
                    if test.get("outcome") == "failed":
                        error_msg = test.get("call", {}).get("longrepr", "Erreur inconnue")
                        errors.append(f"{test.get('nodeid', 'test')}: {error_msg}")
                
                return {
                    "success": failed == 0,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors
                }
    except Exception as e:
        print(f" Erreur lors du parsing du rapport : {str(e)}")
    
    
    print(" Aucun test pytest trouvé, exécution directe des fichiers Python...")
    return run_python_files_directly(test_dir)

def run_python_files_directly(test_dir: str) -> dict:
    """
    Exécute directement tous les fichiers .py du dossier.
    Si aucune erreur → SUCCESS
    
    Args:
        test_dir: Dossier contenant les fichiers
        
    Returns:
        dict: Résultats de l'exécution
    """
    python_files = [f for f in os.listdir(test_dir) if f.endswith('.py') and not f.startswith('__')]
    
    if not python_files:
        return {
            "success": False,
            "passed": 0,
            "failed": 0,
            "errors": ["Aucun fichier Python trouvé dans le dossier"]
        }
    
    passed = 0
    failed = 0
    errors = []
    
    for filename in python_files:
        filepath = os.path.join(test_dir, filename)
        print(f"   Exécution de {filename}...")
        
        
        result = subprocess.run(
            [sys.executable, filepath],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            passed += 1
            print(f"    {filename} exécuté sans erreur")
        else:
            failed += 1
            error_msg = result.stderr if result.stderr else result.stdout
            errors.append(f"{filename}: {error_msg[:500]}")
            print(f"    {filename} a produit une erreur")
    
    return {
        "success": failed == 0,
        "passed": passed,
        "failed": failed,
        "errors": errors
    }