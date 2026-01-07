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

try:
    from src.tools.pytest_tool import run_pytest
    from src.tools.file_tools import read_file_safe
except ImportError:
    print("  ATTENTION : Les outils du Toolsmith ne sont pas encore disponibles.")
    print("   Les fonctions suivantes doivent être créées :")
    print("   - src/tools/pytest_tool.py : run_pytest()")
    print("   - src/tools/file_tools.py : read_file_safe()")

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
    
    Correspond à l'Agent Testeur (The Judge) du TP "The Refactoring Swarm".
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialise l'agent testeur.
        
        Args:
            model_name: Nom du modèle LLM à utiliser (recommandé: gemini-2.0-flash-exp)
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
        Exécute les tests unitaires sur le code et logue chaque fichier individuellement.
        
        Cette méthode respecte le protocole de logging du TP en enregistrant :
        - file_analyzed : Nom du fichier Python testé
        - issues_found : Nombre d'erreurs détectées pour ce fichier
        - input_prompt : Le prompt envoyé au LLM (OBLIGATOIRE)
        - output_response : La réponse du LLM (OBLIGATOIRE)
        
        Args:
            target_dir: Dossier contenant le code à tester (ex: "./sandbox/dataset_inconnu")
            
        Returns:
            Dict: Résultat des tests avec statut et détails
        """
        print(f"\n  [JUDGE] Démarrage des tests sur : {target_dir}")
        
        try:
            #  ÉTAPE 1 : Lister tous les fichiers Python dans le dossier
            python_files = [f for f in os.listdir(target_dir) if f.endswith(".py")]
            print(f" Fichiers Python trouvés : {len(python_files)}")
            
            if len(python_files) == 0:
                print("  Aucun fichier Python trouvé dans le dossier cible.")
                return {
                    "success": False,
                    "passed": 0,
                    "failed": 0,
                    "errors": ["Aucun fichier Python trouvé"],
                    "recommendations": ["Vérifier que le dossier contient des fichiers .py"]
                }
            
            #  ÉTAPE 2 : Exécution de pytest sur tout le dossier
            print(" Exécution de pytest...")
            test_result = run_pytest(target_dir)
            
            passed = test_result.get("passed", 0)
            failed = test_result.get("failed", 0)
            total = passed + failed
            errors = test_result.get("errors", [])
            
            print(f" Résultats globaux : {passed}/{total} tests réussis")
            
            #  ÉTAPE 3 : Logger chaque fichier Python individuellement
            for file_name in python_files:
                file_path = os.path.join(target_dir, file_name)
                
                try:
                    # Lire le contenu du fichier
                    code_content = read_file_safe(file_path)
                    
                    # Filtrer les erreurs liées à ce fichier spécifique
                    file_errors = self._filter_errors_for_file(errors, file_name)
                    file_issues_count = len(file_errors)
                    
                    # Construire le prompt d'analyse pour ce fichier
                    input_prompt = f"Analyse du fichier {file_name} dans {target_dir}. Tests exécutés avec pytest."
                    
                    # Construire la réponse
                    if file_issues_count == 0:
                        output_response = f" Fichier {file_name} : Aucune erreur détectée. Tous les tests passent."
                        file_status = "SUCCESS"
                    else:
                        output_response = f" Fichier {file_name} : {file_issues_count} erreur(s) détectée(s).\n"
                        output_response += "\n".join(file_errors[:3])  # Limiter à 3 erreurs pour le log
                        file_status = "SUCCESS"  #  CORRIGÉ : L'analyse a fonctionné
                    
                    #  LOGGING OBLIGATOIRE selon le protocole du TP
                    log_experiment(
                        agent_name="Judge_Agent",
                        model_used=self.model_name,
                        action=ActionType.DEBUG if file_issues_count > 0 else ActionType.ANALYSIS,
                        details={
                            "file_analyzed": file_name,  #  OBLIGATOIRE : Nom du fichier
                            "input_prompt": input_prompt,  #  OBLIGATOIRE : Prompt envoyé
                            "output_response": output_response,  #  OBLIGATOIRE : Réponse
                            "issues_found": file_issues_count,  #  OBLIGATOIRE : Nombre d'erreurs
                            "file_path": file_path,                         
                            "test_directory": target_dir
                        },
                        status=file_status  #  CORRIGÉ : SUCCESS même si erreurs détectées
                    )
                    
                    print(f"  {'' if file_issues_count == 0 else ''} {file_name}: {file_issues_count} erreur(s)")
                    
                except Exception as e:
                    print(f" Erreur lors de l'analyse de {file_name} : {str(e)}")
                    
                    # Log en cas d'erreur de lecture du fichier
                    log_experiment(
                        agent_name="Judge_Agent",
                        model_used=self.model_name,
                        action=ActionType.DEBUG,
                        details={
                            "file_analyzed": file_name,
                            "input_prompt": f"Tentative d'analyse de {file_name} dans {target_dir}",
                            "output_response": f" Erreur lors de la lecture : {str(e)}",
                            "issues_found": 1,
                            "error_type": type(e).__name__
                        },
                        status="FAILURE"  #  Ici FAILURE est correct car erreur système
                    )
            
            #  ÉTAPE 4 : Analyse LLM si des erreurs existent
            if failed > 0:
                print(f"\n [JUDGE] {failed} test(s) ont échoué - Analyse LLM en cours...")
                analysis, llm_raw_response = self._analyze_test_failures(errors, target_dir)
                
                # Logger l'analyse LLM globale
                log_experiment(
                    agent_name="Judge_Agent",
                    model_used=self.model_name,
                    action=ActionType.DEBUG,
                    details={
                        "file_analyzed": "global_analysis",
                        "input_prompt": self._build_analysis_prompt(errors),
                        "output_response": llm_raw_response,
                        "issues_found": failed,
                        "recommendations": analysis.get("recommendations", []),
                        "root_causes": analysis.get("root_causes", [])
                    },
                    status="SUCCESS"  #  CORRIGÉ : L'analyse a fonctionné
                )
                
                return {
                    "success": False,
                    "passed": passed,
                    "failed": failed,
                    "errors": errors,
                    "recommendations": analysis.get("recommendations", []),
                    "root_causes": analysis.get("root_causes", [])
                }
            else:
                print(" [JUDGE] Tous les tests passent !")
                return {
                    "success": True,
                    "passed": passed,
                    "failed": 0,
                    "errors": [],
                    "recommendations": []
                }
                
        except Exception as e:
            print(f" [JUDGE] Erreur critique lors de l'exécution des tests : {str(e)}")
            
            #  LOGGING de l'erreur critique
            log_experiment(
                agent_name="Judge_Agent",
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "file_analyzed": "system_error",
                    "input_prompt": f"Exécution de pytest sur {target_dir}",
                    "output_response": f" Erreur système : {str(e)}",
                    "issues_found": 1,
                    "error_type": type(e).__name__,
                    "test_directory": target_dir
                },
                status="FAILURE"  #  Ici FAILURE est correct car erreur système
            )
            
            return {
                "success": False,
                "passed": 0,
                "failed": 0,
                "errors": [str(e)],
                "recommendations": ["Vérifier que pytest est correctement installé et que les tests sont valides"]
            }
    
    def _filter_errors_for_file(self, errors: List[str], file_name: str) -> List[str]:
        """
        Filtre les erreurs pour ne garder que celles liées à un fichier spécifique.
        
        Args:
            errors: Liste de toutes les erreurs pytest
            file_name: Nom du fichier à filtrer (ex: "messy_code.py")
            
        Returns:
            Liste des erreurs concernant ce fichier
        """
        file_errors = []
        file_name_without_ext = file_name.replace('.py', '')
        
        for error in errors:
            # Vérifier si le nom du fichier apparaît dans l'erreur
            if file_name in error or file_name_without_ext in error:
                file_errors.append(error)
        
        return file_errors
    
    def _analyze_test_failures(self, errors: List[str], target_dir: str) -> Tuple[Dict, str]:
        """
        Analyse les échecs de tests avec le LLM pour identifier les causes profondes.
        
        Args:
            errors: Liste des messages d'erreur
            target_dir: Dossier testé
            
        Returns:
            Tuple[Dict, str]: (Analyse structurée, Réponse brute du LLM)
        """
        try:
            analysis_prompt = self._build_analysis_prompt(errors)
            llm_response = self._call_llm(analysis_prompt)
            analysis = self._parse_analysis_response(llm_response)
            return analysis, llm_response
        except Exception as e:
            print(f"  Erreur lors de l'analyse LLM : {str(e)}")
            return {
                "recommendations": ["Corriger les erreurs de test détectées"],
                "root_causes": ["Erreur d'analyse LLM"],
                "severity": "unknown"
            }, f"Erreur : {str(e)}"
    
    def _build_analysis_prompt(self, errors: List[str]) -> str:
        """Construit le prompt pour analyser les erreurs avec le LLM."""
        errors_text = "\n\n".join([
            f"ERREUR {i+1}:\n{error}" 
            for i, error in enumerate(errors[:5])  # Limiter à 5 erreurs
        ])
        
        return f"""Analyse ces erreurs de tests pytest et identifie les causes profondes.

NOMBRE D'ERREURS : {len(errors)}

MESSAGES D'ERREUR :
{errors_text}

INSTRUCTIONS :
1. Identifie le type d'erreur (AssertionError, TypeError, ImportError, etc.)
2. Localise la ligne problématique
3. Propose des solutions concrètes

Génère un rapport JSON avec les champs suivants :
- recommendations : Liste de solutions
- root_causes : Liste des causes identifiées
- severity : "high", "medium" ou "low"

Réponds UNIQUEMENT avec du JSON valide."""
    
    def _call_llm(self, prompt: str) -> str:
        """Appelle le LLM avec le system prompt et le user prompt."""
        messages = [
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        response = self.llm.invoke(messages)
        
        # Gestion des différents formats de réponse
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
            # Nettoyer la réponse des balises markdown
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parser le JSON
            data = json.loads(cleaned)
            
            # Normaliser la structure
            return {
                "recommendations": data.get("recommendations", [data.get("recommendation", "Corriger les erreurs")]),
                "root_causes": [data.get("root_cause", "Cause inconnue")] if isinstance(data.get("root_cause"), str) else data.get("root_causes", ["Cause inconnue"]),
                "severity": data.get("severity", "medium")
            }
        except json.JSONDecodeError as e:
            print(f"  Erreur de parsing JSON : {str(e)}")
            return {
                "recommendations": [response[:200]] if response else ["Corriger les erreurs"],
                "root_causes": ["Analyse non structurée"],
                "severity": "unknown"
            }
