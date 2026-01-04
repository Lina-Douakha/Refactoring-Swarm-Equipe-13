"""
Module d'orchestration du Refactoring Swarm.
Gère la coordination entre Auditeur, Correcteur et Testeur.
"""

import os
from typing import Dict
from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent
from src.utils.logger import log_experiment, ActionType


def run_refactoring_swarm(target_dir: str, max_iterations: int = 10) -> Dict:
    """
    Orchestre le cycle complet de refactoring.
    
    FLUX :
    1. Auditeur analyse le code
    2. Correcteur applique les corrections
    3. Testeur valide
    4. Si échec : Retour au Correcteur (Self-Healing Loop)
    5. Si succès : Mission accomplie
    
    Args:
        target_dir: Dossier contenant le code à refactorer
        max_iterations: Nombre max d'itérations (défaut: 10)
        
    Returns:
        Dict: Résultat final avec statut et métriques
    """
    print("\n🐝 [ORCHESTRATOR] Démarrage de l'essaim...")
    
    # Initialiser les agents
    auditor = AuditorAgent(model_name="gemini-2.0-flash-exp")
    fixer = FixerAgent(model_name="gemini-2.0-flash-exp")
    judge = JudgeAgent(model_name="gemini-2.0-flash-exp")
    
    iteration = 0
    all_tests_passed = False
    
    # Logger le début de l'orchestration
    log_experiment(
        agent_name="Orchestrator",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "target_dir": target_dir,
            "max_iterations": max_iterations,
            "input_prompt": f"Orchestration du refactoring sur {target_dir}",
            "output_response": "Essaim initialisé, agents prêts"
        },
        status="SUCCESS"
    )
    
    try:
        # ÉTAPE 1 : Audit Initial
        print("\n" + "="*60)
        print(" PHASE 1 : AUDIT INITIAL")
        print("="*60)
        
        audit_report = auditor.analyze(target_dir)
        
        if audit_report["total_issues"] == 0:
            print("\n✨ Le code est déjà propre ! Passage direct aux tests...")
        else:
            print(f"\n {audit_report['total_issues']} problème(s) détecté(s)")
        
        # BOUCLE DE SELF-HEALING
        while iteration < max_iterations and not all_tests_passed:
            iteration += 1
            print("\n" + "="*60)
            print(f"ITÉRATION {iteration}/{max_iterations}")
            print("="*60)
            
            # ÉTAPE 2 : Correction
            if audit_report["total_issues"] > 0:
                print("\n PHASE 2 : CORRECTION DU CODE")
                fix_result = fixer.fix(audit_report, target_dir)
                print(f" {fix_result['total_fixes']} correction(s) appliquée(s)")
            
            # ÉTAPE 3 : Tests
            print("\n PHASE 3 : VALIDATION PAR TESTS")
            test_result = judge.test(target_dir)
            
            if test_result["success"]:
                #  SUCCÈS !
                all_tests_passed = True
                print("\n TOUS LES TESTS PASSENT !")
                
                log_experiment(
                    agent_name="Orchestrator",
                    model_used="N/A",
                    action=ActionType.DEBUG,
                    details={
                        "iteration": iteration,
                        "input_prompt": f"Validation finale itération {iteration}",
                        "output_response": f"Succès : {test_result['passed']} tests réussis",
                        "tests_passed": test_result["passed"]
                    },
                    status="SUCCESS"
                )
                
                break
            
            else:
                #  ÉCHEC - Self-Healing
                print(f"\n  {test_result['failed']} test(s) échoué(s)")
                print("🔁 Activation du mode Self-Healing...")
                
                # Analyser les erreurs
                for error in test_result.get("errors", [])[:3]:  # Max 3 erreurs
                    print(f"\n   {error[:200]}...")
                
                # Créer un nouveau rapport d'audit basé sur les erreurs
                print("\n Analyse des erreurs pour nouvelle correction...")
                
                # Le Fixer va réessayer avec les erreurs de tests
                for error in test_result.get("errors", []):
                    # Extraire le fichier problématique depuis l'erreur
                    # (simplifié - à améliorer selon format d'erreur pytest)
                    print(f"  🔧 Tentative de correction basée sur l'erreur...")
                
                log_experiment(
                    agent_name="Orchestrator",
                    model_used="N/A",
                    action=ActionType.DEBUG,
                    details={
                        "iteration": iteration,
                        "input_prompt": f"Échec des tests itération {iteration}",
                        "output_response": f"Échec : {test_result['failed']} tests échoués",
                        "failed_tests": test_result["failed"],
                        "errors_sample": test_result.get("errors", [])[:3]
                    },
                    status="FAILURE"
                )
                
                # Si on a atteint le max d'itérations
                if iteration >= max_iterations:
                    print(f"\n  Limite d'itérations atteinte ({max_iterations})")
                    break
        
        # RÉSULTAT FINAL
        final_result = {
            "success": all_tests_passed,
            "iterations_used": iteration,
            "tests_passed": test_result.get("passed", 0) if 'test_result' in locals() else 0,
            "tests_failed": test_result.get("failed", 0) if 'test_result' in locals() else 0,
            "reason": "Tests validés" if all_tests_passed else f"Échec après {iteration} itérations"
        }
        
        print("\n" + "="*60)
        print(" RAPPORT FINAL")
        print("="*60)
        print(f"Itérations utilisées : {iteration}/{max_iterations}")
        print(f"Statut : {' SUCCÈS' if all_tests_passed else ' ÉCHEC'}")
        print("="*60)
        
        return final_result
        
    except Exception as e:
        print(f"\n [ORCHESTRATOR] Erreur fatale : {str(e)}")
        
        log_experiment(
            agent_name="Orchestrator",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "error": str(e),
                "error_type": type(e).__name__,
                "input_prompt": "Orchestration du refactoring",
                "output_response": f"Erreur : {str(e)}"
            },
            status="FAILURE"
        )
        
        return {
            "success": False,
            "iterations_used": iteration,
            "tests_passed": 0,
            "tests_failed": 0,
            "reason": f"Erreur : {str(e)}"
        }