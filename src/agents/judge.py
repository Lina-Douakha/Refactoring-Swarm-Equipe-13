"""
Agent Testeur (The Judge)
Rôle : Exécuter les tests unitaires et valider que le code fonctionne.
"""

import os
from typing import Dict, List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.logger import log_experiment, ActionType
from dotenv import load_dotenv

load_dotenv()

# Import des outils du Toolsmith
try:
    from src.tools.pytest_tool import run_pytest
    from src.tools.file_tools import read_file_safe
except ImportError:
    print("  ATTENTION : Les outils du Toolsmith ne sont pas encore disponibles.")
    print("   Les fonctions suivantes doivent être créées :")
    print("   - src/tools/pytest_tool.py : run_pytest()")
    print("   - src/tools/file_tools.py : read_file_safe()")

# Import du prompt système
try:
    from src.prompts.judge_prompts import JUDGE_SYSTEM_PROMPT
except ImportError:
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
    "recommendations": ["Corriger X", "Vérifier Y"],
    "root_causes": ["Cause 1", "Cause 2"],
    "severity": "high"
}

Réponds UNIQUEMENT avec du JSON valide."""


class JudgeAgent:
    """
    Agent responsable de l'exécution et validation des tests.
    Valide que le code corrigé fonctionne correctement.
    """
    
    def __init__(self, model_name: str = "gemini-1.5-pro-latest"):
        """
        Initialise l'agent testeur.
        
        Args:
            model_name: Nom du modèle LLM à utiliser
        """
        self.model_name = model_name
        
        api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError(
                " Clé API Google non trouvée. "
                "Assurez-vous d'avoir GOOGLE_API_KEY dans votre fichier .env"
            )
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.1,
        )
        print(f"  JudgeAgent initialisé avec le modèle : {model_name}")
    
    def test(self, target_dir: str) -> Dict:
        """
        Exécute les tests unitaires sur le code.
        
        Args:
            target_dir: Dossier contenant le code à tester
            
        Returns:
            Dict: Résultat des tests avec statut et détails
        """
        print(f"\n  [JUDGE] Démarrage des tests sur : {target_dir}")
        
        try:
            # Étape 1 : Exécuter pytest
            print(" Exécution de pytest...")
            test_result = run_pytest(target_dir)
            
            passed = test_result.get("passed", 0)
            failed = test_result.get("failed", 0)
            total = passed + failed
            
            print(f" Résultats : {passed}/{total} tests réussis")
            
            # Étape 2 : Analyser les résultats
            if test_result.get("success", False):
                print(" [JUDGE] Tous les tests passent !")
                
                result = {
                    "success": True,
                    "passed": passed,
                    "failed": 0,
                    "errors": [],
                    "recommendations": []
                }
                
                
                
                log_experiment(
                    agent_name="Judge_Agent",
                    model_used=self.model_name,
                    action=ActionType.ANALYSIS,  
                    details={
                        "test_directory": target_dir,
                        "input_prompt": f"Exécution et validation de pytest dans {target_dir}",
                        "output_response": f"Résultat: {passed} tests réussis sur {total}. Tous les tests passent.",
                        "passed": passed,
                        "failed": 0,
                        "total": total
                    },
                    status="SUCCESS"
                )
                
                return result
            
            else:
                print(f" [JUDGE] {failed} test(s) ont échoué")
                
                errors = test_result.get("errors", [])
                
                print(" Analyse des erreurs avec le LLM...")
                analysis, llm_raw_response = self._analyze_test_failures(errors, target_dir)
                
                result = {
                    "success": False,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "recommendations": analysis.get("recommendations", []),
                    "root_causes": analysis.get("root_causes", [])
                }
                
                log_experiment(
                    agent_name="Judge_Agent",
                    model_used=self.model_name,
                    action=ActionType.DEBUG,
                    details={
                        "test_directory": target_dir,
                        "input_prompt": self._build_analysis_prompt(errors),
                        "output_response": llm_raw_response,
                        "passed": passed,
                        "failed": failed,
                        "errors_sample": errors[:3] if len(errors) > 3 else errors
                    },
                    status="FAILURE"
                )
                
                return result
                
        except Exception as e:
            print(f" [JUDGE] Erreur lors de l'exécution des tests : {str(e)}")
            
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
            
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "errors": [str(e)],
                "recommendations": ["Vérifier que pytest est correctement installé et que les tests sont valides"]
            }
    
    def _analyze_test_failures(self, errors: List[str], target_dir: str) -> Tuple[Dict, str]:
        """Analyse les échecs de tests avec le LLM."""
        try:
            analysis_prompt = self._build_analysis_prompt(errors)
            llm_response = self._call_llm(analysis_prompt)
            analysis = self._parse_analysis_response(llm_response)
            return analysis, llm_response
        except Exception as e:
            print(f"  Erreur lors de l'analyse LLM : {str(e)}")
            return {
                "recommendations": ["Corriger les erreurs de test"],
                "root_causes": ["Erreur d'analyse"]
            }, f"Erreur : {str(e)}"
    
    def _build_analysis_prompt(self, errors: List[str]) -> str:
        """Construit le prompt pour analyser les erreurs."""
        errors_text = "\n\n".join([
            f"ERREUR {i+1}:\n{error}" 
            for i, error in enumerate(errors[:5])
        ])
        
        return f"""Analyse ces erreurs de tests pytest.

NOMBRE D'ERREURS : {len(errors)}

MESSAGES D'ERREUR :
{errors_text}

Génère un rapport JSON avec recommendations et root_causes."""
    
    def _call_llm(self, prompt: str) -> str:
        """Appelle le LLM."""
        messages = [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        response = self.llm.invoke(messages)
        
        if isinstance(response.content, list):
            content = response.content[0] if response.content else ""
            if hasattr(content, 'text'):
                return content.text
            return str(content)
        
        return response.content
    
    def _parse_analysis_response(self, response: str) -> Dict:
        """Parse la réponse JSON du LLM."""
        import json
        
        if not isinstance(response, str):
            print(f"  Réponse LLM inattendue (type: {type(response)})")
            return {
                "recommendations": ["Corriger les erreurs de test"],
                "root_causes": ["Format de réponse LLM inattendu"],
                "severity": "unknown"
            }
        
        try:
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            data = json.loads(cleaned)
            
            return {
                "recommendations": data.get("recommendations", [data.get("recommendation", "Corriger les erreurs")]),
                "root_causes": [data.get("root_cause", "Cause inconnue")] if isinstance(data.get("root_cause"), str) else data.get("root_causes", ["Cause inconnue"]),
                "severity": data.get("severity", "medium")
            }
        except json.JSONDecodeError:
            return {
                "recommendations": [response[:200]] if response else ["Corriger les erreurs"],
                "root_causes": ["Analyse non structurée"],
                "severity": "unknown"
            }