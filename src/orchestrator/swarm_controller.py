"""
Swarm Controller
Rôle : Orchestrer les 3 agents (Auditor, Fixer, Judge) dans une boucle itérative
"""

import os
import argparse
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent


from src.utils.logger import log_experiment, ActionType


def run_refactoring_swarm(
    target_dir: str,
    model_name: str = "gemini-2.0-flash-exp",
    max_iterations: int = 10,
    generate_tests: bool = True,
    generate_docs: bool = False
) -> Dict:
    """
    Fonction principale d'orchestration du Swarm.
    
    Workflow :
    1. Auditor analyse le code (ActionType.ANALYSIS)
    2. Fixer corrige selon le rapport (ActionType.FIX)
    3. Fixer génère les tests manquants (ActionType.GENERATION) [optionnel]
    4. Judge valide avec les tests (ActionType.DEBUG/ANALYSIS)
    5. Répète jusqu'à succès ou max_iterations
    6. Fixer génère la documentation (ActionType.GENERATION) [optionnel]
    
    Args:
        target_dir: Dossier contenant le code à refactoriser
        model_name: Nom du modèle LLM à utiliser
        max_iterations: Nombre maximum d'itérations (défaut: 10)
        generate_tests: Générer automatiquement les tests unitaires manquants
        generate_docs: Générer automatiquement la documentation
    
    Returns:
        Dict: Résultats finaux avec statut et statistiques
    """
    
    print("="*80)
    print(" DÉMARRAGE DU SWARM DE REFACTORISATION")
    print("="*80)
    print(f" Dossier cible : {target_dir}")
    print(f" Modèle LLM : {model_name}")
    print(f" Itérations max : {max_iterations}")
    print(f" Génération tests : {'' if generate_tests else ''}")
    print(f" Génération docs : {'' if generate_docs else ''}")
    print("="*80)
    
    
    if not os.path.exists(target_dir):
        raise FileNotFoundError(f" Le dossier {target_dir} n'existe pas")
    
    
    
    
    print("\n Initialisation des agents...")
    auditor = AuditorAgent(model_name=model_name)
    fixer = FixerAgent(model_name=model_name)
    judge = JudgeAgent(model_name=model_name)
    print(" Tous les agents sont prêts\n")
    
    
    iteration = 0
    all_tests_passed = False
    history = []
    
    
    
    
    while iteration < max_iterations and not all_tests_passed:
        iteration += 1
        
        print("\n" + "="*80)
        print(f" ITÉRATION {iteration}/{max_iterations}")
        print("="*80)
        
        try:
            
            
            
            print("\n ÉTAPE 1/4 : Analyse du code par l'Auditor")
            print("-"*80)
            
            audit_report = auditor.analyze(target_dir=target_dir)
            
            print(f"\n Analyse terminée :")
            print(f"    Fichiers analysés : {len(audit_report['files_analyzed'])}")
            print(f"    Problèmes détectés : {audit_report['total_issues']}")
            
            if audit_report['total_issues'] > 0:
                print(f"\n Recommandations :")
                for rec in audit_report.get('recommendations', [])[:3]:
                    print(f"   - {rec}")
            
            
            
            
            print("\n ÉTAPE 2/4 : Correction du code par le Fixer")
            print("-"*80)
            
            if audit_report['total_issues'] == 0:
                print(" Aucun problème à corriger, passage direct aux tests")
                fix_result = {
                    "files_fixed": [],
                    "total_fixes": 0,
                    "status": "no_issues"
                }
            else:
                fix_result = fixer.fix(
                    audit_report=audit_report,
                    target_dir=target_dir
                )
                
                print(f"\n Corrections terminées :")
                print(f"    Fichiers corrigés : {len(fix_result['files_fixed'])}")
                print(f"    Corrections appliquées : {fix_result['total_fixes']}")
                
                if fix_result['files_fixed']:
                    print(f"    Fichiers modifiés : {', '.join(fix_result['files_fixed'])}")
            
            
            
            
            if generate_tests and iteration == 1:  
                print("\n ÉTAPE 3/4 : Génération des tests unitaires manquants")
                print("-"*80)
                
                
                python_files = [
                    f for f in os.listdir(target_dir)
                    if f.endswith(".py") and not f.startswith("test_") and f != "__init__.py"
                ]
                
                tests_generated = []
                
                for filename in python_files:
                    test_filename = f"test_{filename}"
                    test_filepath = os.path.join(target_dir, test_filename)
                    
                    
                    if not os.path.exists(test_filepath):
                        print(f"    Génération de tests pour {filename}...")
                        try:
                            fixer.generate_tests(filename, target_dir)
                            tests_generated.append(test_filename)
                            print(f"       {test_filename} créé")
                        except Exception as e:
                            print(f"       Échec : {str(e)}")
                    else:
                        print(f"    Tests déjà présents pour {filename}")
                
                if tests_generated:
                    print(f"\n {len(tests_generated)} fichier(s) de tests généré(s)")
                else:
                    print(f"\n Tous les fichiers ont déjà leurs tests")
            else:
                print("\n  ÉTAPE 3/4 : Génération de tests (ignorée)")
            
            
            
            
            print("\n ÉTAPE 4/4 : Validation par le Judge")
            print("-"*80)
            
            test_result = judge.test(target_dir=target_dir)
            
            print(f"\n Résultats des tests :")
            print(f"    Tests réussis : {test_result['passed']}")
            print(f"    Tests échoués : {test_result['failed']}")
            
            
            
            
            if test_result["success"]:
                all_tests_passed = True
                print("\n SUCCÈS ! Tous les tests passent ! ")
                print("="*80)
                break
            else:
                print(f"\n  {test_result['failed']} test(s) ont échoué")
                print(" Nouvelle itération nécessaire...")
                
                
                if test_result.get("recommendations"):
                    print("\n Recommandations du Judge :")
                    for rec in test_result["recommendations"][:5]:
                        print(f"   - {rec}")
                
                
                if iteration < max_iterations:
                    print("\n Tentative de correction avec feedback des tests...")
                    
                    
                    errors = test_result.get("errors", [])
                    python_files = [
                        f for f in os.listdir(target_dir)
                        if f.endswith(".py") and not f.startswith("test_")
                    ]
                    
                    problematic_files = set()
                    for error in errors:
                        for pfile in python_files:
                            if pfile in error or pfile.replace('.py', '') in error:
                                problematic_files.add(pfile)
                    
                    
                    for filename in problematic_files:
                        filepath = os.path.join(target_dir, filename)
                        
                        
                        file_errors = [e for e in errors if filename in e]
                        error_message = "\n".join(file_errors[:3])  
                        
                        print(f"    Correction de {filename}...")
                        try:
                            fixer.retry_fix(filepath, target_dir, error_message)
                            print(f"       Nouvelle version générée")
                        except Exception as e:
                            print(f"       Échec : {str(e)}")
            
            
            history.append({
                "iteration": iteration,
                "issues_detected": audit_report['total_issues'],
                "fixes_applied": fix_result.get('total_fixes', 0),
                "tests_passed": test_result['passed'],
                "tests_failed": test_result['failed']
            })
            
        except Exception as e:
            print(f"\n ERREUR lors de l'itération {iteration} : {str(e)}")
            
            
            log_experiment(
                agent_name="Swarm_Controller",
                model_used=model_name,
                action=ActionType.DEBUG,
                details={
                    "file_analyzed": f"iteration_{iteration}",
                    "input_prompt": f"Orchestration itération {iteration} sur {target_dir}",
                    "output_response": f"Erreur : {str(e)}",
                    "issues_found": 1,
                    "error_type": type(e).__name__,
                    "iteration": iteration
                },
                status="FAILURE"
            )
            
            import traceback
            traceback.print_exc()
            break
    
    
    
    
    if all_tests_passed and generate_docs:
        print("\n" + "="*80)
        print(" GÉNÉRATION DE LA DOCUMENTATION")
        print("="*80)
        
        python_files = [
            f for f in os.listdir(target_dir)
            if f.endswith(".py") and not f.startswith("test_") and f != "__init__.py"
        ]
        
        for filename in python_files:
            doc_filename = f"README_{filename.replace('.py', '')}.md"
            doc_filepath = os.path.join(target_dir, doc_filename)
            
            if not os.path.exists(doc_filepath):
                print(f"\n Génération de documentation pour {filename}...")
                try:
                    fixer.generate_documentation(filename, target_dir)
                    print(f"    {doc_filename} créé")
                except Exception as e:
                    print(f"    Échec : {str(e)}")
            else:
                print(f" Documentation déjà présente pour {filename}")
    
    
    
    
    print("\n" + "="*80)
    print(" FIN DU SWARM - RAPPORT FINAL")
    print("="*80)
    
    final_result = {
        "success": all_tests_passed,
        "total_iterations": iteration,
        "max_iterations_reached": iteration >= max_iterations and not all_tests_passed,
        "history": history,
        "target_dir": target_dir,
        "model_used": model_name
    }
    
    if all_tests_passed:
        print(f"\n MISSION ACCOMPLIE en {iteration} itération(s) ! ")
        print(f"    Tous les tests passent avec succès")
        if generate_tests:
            print(f"    Tests unitaires générés")
        if generate_docs:
            print(f"    Documentation générée")
    else:
        print(f"\n ÉCHEC après {iteration} itération(s)")
        if iteration >= max_iterations:
            print(f"    Nombre maximum d'itérations atteint ({max_iterations})")
        print(f"    Certains tests échouent encore")
    
    print("\n STATISTIQUES PAR ITÉRATION :")
    print("-"*80)
    for i, iter_data in enumerate(history, 1):
        print(f"   Itération {i} :")
        print(f"       Problèmes détectés : {iter_data['issues_detected']}")
        print(f"       Corrections appliquées : {iter_data['fixes_applied']}")
        print(f"       Tests réussis : {iter_data['tests_passed']}")
        print(f"       Tests échoués : {iter_data['tests_failed']}")
    
    print("\n" + "="*80)
    
    return final_result


def main():
    """
    Point d'entrée principal avec gestion des arguments CLI.
    Conforme aux exigences du TP (argument --target_dir obligatoire).
    """
    
    parser = argparse.ArgumentParser(
        description=" The Refactoring Swarm - Système multi-agents de refactorisation automatique",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation :
  python main.py --target_dir ./sandbox/messy_code
  python main.py --target_dir ./sandbox/dataset_inconnu --max_iterations 5
  python main.py --target_dir ./sandbox --generate_tests --generate_docs
        """
    )
    
    
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help=" Dossier contenant le code à refactoriser (OBLIGATOIRE)"
    )
    
    
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.0-flash-exp",
        help=" Nom du modèle LLM à utiliser (défaut: gemini-2.0-flash-exp)"
    )
    
    parser.add_argument(
        "--max_iterations",
        type=int,
        default=10,
        help=" Nombre maximum d'itérations (défaut: 10)"
    )
    
    parser.add_argument(
        "--generate_tests",
        action="store_true",
        help=" Générer automatiquement les tests unitaires manquants"
    )
    
    parser.add_argument(
        "--generate_docs",
        action="store_true",
        help=" Générer automatiquement la documentation"
    )
    
    parser.add_argument(
        "--no_generation",
        action="store_true",
        help=" Désactiver toute génération automatique (tests et docs)"
    )
    
    args = parser.parse_args()
    
    
    if args.no_generation:
        generate_tests = False
        generate_docs = False
    else:
        generate_tests = args.generate_tests
        generate_docs = args.generate_docs
    
    try:
        result = run_refactoring_swarm(
            target_dir=args.target_dir,
            model_name=args.model,
            max_iterations=args.max_iterations,
            generate_tests=generate_tests,
            generate_docs=generate_docs
        )
        
        
        if result["success"]:
            print("\n Le code a été refactorisé avec succès !")
            exit(0)
        else:
            print("\n La refactorisation a échoué")
            exit(1)
            
    except Exception as e:
        print(f"\n ERREUR CRITIQUE : {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
