"""
Agent Testeur (The Judge)
Rôle : Exécuter les tests unitaires et valider que le code fonctionne.
"""

import os
from typing import Dict, List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.logger import log_experiment, ActionType
from dotenv import load_dotenv  
# Import des outils du Toolsmith
try:
    from src.tools.pytest_tool import run_pytest
    from src.tools.file_tools import read_file_safe
except ImportError:
    print("   ATTENTION : Les outils du Toolsmith ne sont pas encore disponibles.")
    print("   Les fonctions suivantes doivent être créées :")
    print("   - src/tools/pytest_tool.py : run_pytest()")
    print("   - src/tools/file_tools.py : read_file_safe()")

# Import du prompt système
try:
    from src.prompts.judge_prompts import JUDGE_SYSTEM_PROMPT
except ImportError:
    # Prompt de secours
    JUDGE_SYSTEM_PROMPT = """Tu es un expert en debugging Python et analyse de tests.

MISSION :
Analyse les résultats de tests pytest et identifie la cause des échecs.

INSTRUCTIONS :
1. Lis attentivement les messages d'erreur
2. Identifie le type d'erreur (AssertionError, TypeError, etc.)
3. Localise la ligne problématique
4. Propose une solution claire et précise

FORMAT DE SORTIE (JSON) :
{
    "error_type": "AssertionError",
    "affected_function": "test_add",
    "root_cause": "La fonction add() retourne un string au lieu d'un int",
    "recommendation": "Convertir le résultat en int avant de le retourner",
    "severity": "high"
}

Réponds UNIQUEMENT avec du JSON valide."""


class JudgeAgent:
    """
    Agent responsable de l'exécution et validation des tests.
    Valide que le code corrigé fonctionne correctement.
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialise l'agent testeur.
        
        Args:
            model_name: Nom du modèle LLM à utiliser
        """
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1,  # Basse température pour analyse précise
        )
        print(f"⚖️  JudgeAgent initialisé avec le modèle : {model_name}")
    
    def test(self, target_dir: str) -> Dict:
        """
        Exécute les tests unitaires sur le code.
        
        Args:
            target_dir: Dossier contenant le code à tester
            
        Returns:
            Dict: Résultat des tests avec statut et détails
        """
        print(f"\n⚖️  [JUDGE] Démarrage des tests sur : {target_dir}")
        
        try:
            # Étape 1 : Exécuter pytest
            print("🧪 Exécution de pytest...")
            test_result = run_pytest(target_dir)
            
            passed = test_result.get("passed", 0)
            failed = test_result.get("failed", 0)
            total = passed + failed
            
            print(f" Résultats : {passed}/{total} tests réussis")
            
            # Étape 2 : Analyser les résultats
            if test_result.get("success", False):
                #    SUCCÈS - Tous les tests passent
                print("🎉 [JUDGE] Tous les tests passent !")
                
                result = {
                    "success": True,
                    "passed": passed,
                    "failed": 0,
                    "errors": [],
                    "recommendations": []
                }
                
                # Logger le succès
                log_experiment(
                    agent_name="Judge_Agent",
                    model_used=self.model_name,
                    action=ActionType.DEBUG,
                    details={
                        "test_directory": target_dir,
                        "input_prompt": f"Validation des tests dans {target_dir}",
                        "output_response": f"Tous les tests réussis : {passed}/{total}",
                        "passed": passed,
                        "failed": 0
                    },
                    status="SUCCESS"
                )
                
                return result
            
            else:
                #    ÉCHEC - Des tests ont échoué
                print(f"   [JUDGE] {failed} test(s) ont échoué")
                
                errors = test_result.get("errors", [])
                
                # Étape 3 : Analyser les erreurs avec le LLM
                print("  Analyse des erreurs avec le LLM...")
                
                #    CORRECTION ICI : Récupérer les DEUX valeurs
                analysis, llm_raw_response = self._analyze_test_failures(errors, target_dir)
                
                result = {
                    "success": False,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "recommendations": analysis.get("recommendations", []),
                    "root_causes": analysis.get("root_causes", [])
                }
                
                # Logger l'échec
                log_experiment(
                    agent_name="Judge_Agent",
                    model_used=self.model_name,
                    action=ActionType.DEBUG,
                    details={
                        "test_directory": target_dir,
                        "input_prompt": self._build_analysis_prompt(errors),
                        "output_response": llm_raw_response,  #    RÉPONSE BRUTE DU LLM
                        "passed": passed,
                        "failed": failed,
                        "errors_sample": errors[:3] if len(errors) > 3 else errors
                    },
                    status="FAILURE"
                )
                
                return result
                
        except Exception as e:
            print(f"   [JUDGE] Erreur lors de l'exécution des tests : {str(e)}")
            
            log_experiment(
                agent_name="Judge_Agent",
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "test_directory": target_dir,
                    "input_prompt": f"Exécution de pytest sur {target_dir}",
                    "output_response": f"Erreur : {str(e)}",
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            
            # Retourner un échec avec l'erreur
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "errors": [str(e)],
                "recommendations": ["Vérifier que pytest est correctement installé et que les tests sont valides"]
            }
    
    def _analyze_test_failures(self, errors: List[str], target_dir: str) -> Tuple[Dict, str]:
        """
        Analyse les échecs de tests avec le LLM.
        
        Args:
            errors: Liste des messages d'erreur
            target_dir: Dossier contenant le code
            
        Returns:
            Tuple[Dict, str]: (analyse_structurée, réponse_brute_du_LLM)
        """
        try:
            # Construire le prompt d'analyse
            analysis_prompt = self._build_analysis_prompt(errors)
            
            # Appeler le LLM
            llm_response = self._call_llm(analysis_prompt)
            
            # Parser la réponse
            analysis = self._parse_analysis_response(llm_response)
            
            #    Retourner les DEUX : le dictionnaire ET la réponse brute
            return analysis, llm_response
            
        except Exception as e:
            print(f"   Erreur lors de l'analyse LLM : {str(e)}")
            return {
                "recommendations": ["Corriger les erreurs de test"],
                "root_causes": ["Erreur d'analyse"]
            }, f"Erreur : {str(e)}"
    
    def _build_analysis_prompt(self, errors: List[str]) -> str:
        """
        Construit le prompt pour analyser les erreurs de tests.
        
        Args:
            errors: Liste des messages d'erreur
            
        Returns:
            str: Prompt formaté pour le LLM
        """
        errors_text = "\n\n".join([
            f"ERREUR {i+1}:\n{error}" 
            for i, error in enumerate(errors[:5])  # Limiter à 5 erreurs max
        ])
        
        return f"""Analyse ces erreurs de tests pytest et identifie les causes.

NOMBRE D'ERREURS : {len(errors)}

MESSAGES D'ERREUR :
{errors_text}

INSTRUCTIONS :
1. Identifie le type d'erreur (AssertionError, TypeError, NameError, etc.)
2. Localise la fonction/ligne problématique
3. Détermine la cause racine
4. Propose une solution concrète

Génère un rapport JSON avec :
- recommendations : liste de solutions
- root_causes : liste des causes identifiées
- severity : "low", "medium" ou "high"
"""
    
    def _call_llm(self, prompt: str) -> str:
        """
        Appelle le LLM pour analyser les erreurs.
        
        Args:
            prompt: Prompt utilisateur
            
        Returns:
            str: Analyse du LLM
        """
        messages = [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """
        Parse la réponse JSON du LLM.
        
        Args:
            response: Réponse brute du LLM
            
        Returns:
            Dict: Analyse structurée
        """
        import json
        
        try:
            # Nettoyer la réponse
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            data = json.loads(cleaned)
            
            # Extraire les informations pertinentes
            return {
                "recommendations": data.get("recommendations", [data.get("recommendation", "Corriger les erreurs")]),
                "root_causes": [data.get("root_cause", "Cause inconnue")],
                "severity": data.get("severity", "medium")
            }
            
        except json.JSONDecodeError:
            print("   Impossible de parser la réponse JSON du LLM")
            # Extraire au moins du texte utile
            return {
                "recommendations": [response[:200]] if response else ["Corriger les erreurs de test"],
                "root_causes": ["Analyse non structurée"],
                "severity": "unknown"
            }
    
    def validate_code_quality(self, target_dir: str, min_score: float = 7.0) -> bool:
        """
        BONUS : Valide la qualité du code avec pylint (optionnel).
        
        Args:
            target_dir: Dossier à valider
            min_score: Score minimum acceptable (sur 10)
            
        Returns:
            bool: True si la qualité est acceptable
        """
        print(f"\n [JUDGE] Validation de la qualité du code (score minimum : {min_score}/10)")
        
        try:
            from src.tools.pylint_tool import run_pylint
            from src.tools.file_tools import list_python_files
            
            python_files = list_python_files(target_dir)
            total_score = 0
            
            for filepath in python_files:
                result = run_pylint(filepath)
                score = result.get("score", 0)
                total_score += score
                print(f"  - {os.path.basename(filepath)}: {score}/10")
            
            average_score = total_score / len(python_files) if python_files else 0
            print(f"\n Score moyen : {average_score:.2f}/10")
            
            return average_score >= min_score
            
        except Exception as e:
            print(f"  Validation de qualité impossible : {str(e)}")
            return True  # Ne pas bloquer si la validation échoue