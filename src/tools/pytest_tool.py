import subprocess
import json
import os

def run_pytest(test_dir: str) -> dict:
    """
    Exécute pytest sur un dossier et retourne les résultats.
    
    Args:
        test_dir: Dossier contenant les tests
        
    Returns:
        dict: Résultats des tests
    """
    # Chemin du rapport JSON
    report_path = os.path.join(test_dir, ".report.json")
    
    # Exécuter pytest avec génération de rapport JSON
    result = subprocess.run(
        [
            "pytest", 
            test_dir, 
            f"--json-report",
            f"--json-report-file={report_path}",
            "--tb=short"
        ],
        capture_output=True,
        text=True
    )
    
    # Parser les résultats
    return parse_test_results(report_path, result.stdout, result.stderr)

def parse_test_results(report_path: str, stdout: str, stderr: str) -> dict:
    """
    Parse les résultats de pytest.
    
    Args:
        report_path: Chemin du fichier de rapport JSON
        stdout: Sortie standard de pytest
        stderr: Sortie d'erreur de pytest
        
    Returns:
        dict: Résultats structurés
    """
    try:
        # Essayer de lire le rapport JSON
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            
            tests = report.get("tests", [])
            passed = sum(1 for t in tests if t.get("outcome") == "passed")
            failed = sum(1 for t in tests if t.get("outcome") == "failed")
            
            # Extraire les messages d'erreur
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
        print(f"⚠️ Erreur lors du parsing du rapport : {str(e)}")
    
    # Fallback : Parser la sortie texte de pytest
    if "passed" in stdout or "PASSED" in stdout:
        # Extraction basique depuis la sortie texte
        return {
            "success": "failed" not in stdout.lower() and "error" not in stdout.lower(),
            "passed": stdout.count("PASSED"),
            "failed": stdout.count("FAILED"),
            "errors": [line for line in stdout.split("\n") if "FAILED" in line or "ERROR" in line]
        }
    
    # Si tout échoue
    return {
        "success": False,
        "passed": 0,
        "failed": 0,
        "errors": [f"Impossible de parser les résultats. STDOUT: {stdout[:200]}"]
    }