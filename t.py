"""
Swarm Controller
Rôle : Orchestrer les 3 agents (Auditor, Fixer, Judge) dans une boucle itérative
"""

import os
from typing import Dict
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Import des agents
from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent

# Import du logger
from src.utils.logger import log_experiment, ActionType


def run_refactoring_swarm(
    target_dir: str,
    model_name: str = "gemini-2.5-flash",
    max_iterations: int = 10
) -> Dict:
    """
    Fonction principale d'orchestration du Swarm.
    
    Workflow :
    1. Auditor analyse le code
    2. Fixer corrige selon le rapport
    3. Judge valide avec les tests
    4. Répète jusqu'à succès ou max_iterations
    
    Args:
        target_dir: Dossier contenant le code à refactoriser
        model_name: Nom du modèle LLM à utiliser
        max_iterations: Nombre maximum d'itérations (défaut: 10)
    
    Returns:
        Dict: Résultats finaux avec statut et statistiques
    """
    
    print("="*70)
    print(" DÉMARRAGE DU SWARM DE REFACTORISATION")
    print("="*70)
    print(f" Dossier cible : {target_dir}")
    print(f" Modèle LLM : {model_name}")
    print(f" Itérations max : {max_iterations}")
    print("="*70)
    
    # Vérifier que le dossier existe
    if not os.path.exists(target_dir):
        raise FileNotFoundError(f" Le dossier {target_dir} n'existe pas")
    
    # Initialiser les agents
    print("\n Initialisation des agents...")
    auditor = AuditorAgent(model_name=model_name)
    fixer = FixerAgent(model_name=model_name)
    judge = JudgeAgent(model_name=model_name)
    print(" Tous les agents sont prêts\n")
    
    # Variables de suivi
    iteration = 0
    all_tests_passed = False
    history = []
    
    # Boucle principale
    while iteration < max_iterations and not all_tests_passed:
        iteration += 1
        
        print("\n" + "="*70)
        print(f" ITÉRATION {iteration}/{max_iterations}")
        print("="*70)
        
        try:
            # ========================================
            # ÉTAPE 1 : AUDITOR - Analyse du code
            # ========================================
            print("\n ÉTAPE 1/3 : Analyse du code par l'Auditor")
            print("-"*70)
            
            audit_report = auditor.analyze(target_dir=target_dir)
            
            print(f"\n Analyse terminée :")
            print(f"   - Fichiers analysés : {len(audit_report['files_analyzed'])}")
            print(f"   - Problèmes détectés : {audit_report['total_issues']}")
            
            # ========================================
            # ÉTAPE 2 : FIXER - Correction du code
            # ========================================
            print("\n ÉTAPE 2/3 : Correction du code par le Fixer")
            print("-"*70)
            
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
                print(f"   - Fichiers corrigés : {len(fix_result['files_fixed'])}")
                print(f"   - Corrections appliquées : {fix_result['total_fixes']}")
            
            # ========================================
            # ÉTAPE 3 : JUDGE - Validation par tests
            # ========================================
            print("\n  ÉTAPE 3/3 : Validation par le Judge")
            print("-"*70)
            
            test_result = judge.test(target_dir=target_dir)
            
            print(f"\n Résultats des tests :")
            print(f"   - Tests réussis : {test_result['passed']}")
            print(f"   - Tests échoués : {test_result['failed']}")
            
            # ========================================
            # DÉCISION : Continuer ou arrêter ?
            # ========================================
            if test_result["success"]:
                all_tests_passed = True
                print("\n SUCCÈS ! Tous les tests passent !")
                print("="*70)
                break
            else:
                print(f"\n  {test_result['failed']} test(s) ont échoué")
                print(" Nouvelle itération nécessaire...")
                
                # Afficher les recommandations du Judge
                if test_result.get("recommendations"):
                    print("\n Recommandations du Judge :")
                    for rec in test_result["recommendations"]:
                        print(f"   - {rec}")
            
            # Enregistrer l'itération dans l'historique
            history.append({
                "iteration": iteration,
                "issues_detected": audit_report['total_issues'],
                "fixes_applied": fix_result.get('total_fixes', 0),
                "tests_passed": test_result['passed'],
                "tests_failed": test_result['failed']
            })
            
        except Exception as e:
            print(f"\n ERREUR lors de l'itération {iteration} : {str(e)}")
            
            # Logger l'erreur
            log_experiment(
                agent_name="Swarm_Controller",
                model_used=model_name,
                action=ActionType.DEBUG,
                details={
                    "iteration": iteration,
                    "input_prompt": f"Orchestration itération {iteration}",
                    "output_response": f"Erreur : {str(e)}",
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            
            break
    
    # ========================================
    # RÉSULTAT FINAL
    # ========================================
    print("\n" + "="*70)
    print(" FIN DU SWARM")
    print("="*70)
    
    final_result = {
        "success": all_tests_passed,
        "total_iterations": iteration,
        "max_iterations_reached": iteration >= max_iterations and not all_tests_passed,
        "history": history
    }
    
    if all_tests_passed:
        print(f"\n MISSION ACCOMPLIE en {iteration} itération(s) !")
        print(f"   Tous les tests passent avec succès.")
    else:
        print(f"\n  ÉCHEC après {iteration} itération(s)")
        if iteration >= max_iterations:
            print(f"   Nombre maximum d'itérations atteint ({max_iterations})")
        print(f"   Certains tests échouent encore.")
    
    print("\n STATISTIQUES :")
    for i, iter_data in enumerate(history, 1):
        print(f"   Itération {i} :")
        print(f"      - Problèmes détectés : {iter_data['issues_detected']}")
        print(f"      - Corrections appliquées : {iter_data['fixes_applied']}")
        print(f"      - Tests réussis/échoués : {iter_data['tests_passed']}/{iter_data['tests_failed']}")
    
    print("\n" + "="*70)
    
    return final_result


# ========================================
# FONCTION DE LANCEMENT RAPIDE
# ========================================
def main():
    """Point d'entrée principal pour tester le Swarm"""
    
    # Configuration
    TARGET_DIR = "sandbox"  # Dossier à refactoriser
    MODEL_NAME = "gemini-2.5-flash"
    MAX_ITERATIONS = 10
    
    # Lancer le Swarm
    try:
        result = run_refactoring_swarm(
            target_dir=TARGET_DIR,
            model_name=MODEL_NAME,
            max_iterations=MAX_ITERATIONS
        )
        
        # Afficher le résultat
        if result["success"]:
            print("\n Le code a été refactorisé avec succès !")
            exit(0)
        else:
            print("\n La refactorisation a échoué")
            exit(1)
            
    except Exception as e:
        print(f"\n ERREUR CRITIQUE : {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()