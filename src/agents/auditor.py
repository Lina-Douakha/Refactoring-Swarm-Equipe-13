"""
Agent Auditeur (The Auditor)
Rôle : Analyser le code Python, détecter les problèmes de qualité et générer un rapport.
"""

import os
from dotenv import load_dotenv 
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.logger import log_experiment, ActionType

load_dotenv()

from src.tools.file_tools import read_file_safe, list_python_files
from src.tools.pylint_tool import run_pylint, parse_pylint_output

try:
    from src.prompts.auditor_prompts import AUDITOR_SYSTEM_PROMPT
except ImportError:
    AUDITOR_SYSTEM_PROMPT = """Tu es un expert Python chargé d'analyser du code.

MISSION :
Analyse le code fourni et les rapports pylint, puis génère un rapport JSON.

FORMAT DE SORTIE (STRICT) :
{
    "files_analyzed": ["file1.py", "file2.py"],
    "total_issues": 5,
    "issues": [
        {
            "file": "example.py",
            "line": 10,
            "severity": "high",
            "type": "missing_docstring",
            "message": "La fonction manque de docstring"
        }
    ],
    "recommendations": ["Ajouter des docstrings", "Corriger la syntaxe"]
}

Réponds UNIQUEMENT avec du JSON valide, sans texte avant ou après."""


class AuditorAgent:
    """
    Agent responsable de l'audit du code.
    Analyse la qualité, détecte les bugs et génère un rapport.
    
    Correspond à l'Agent Auditeur (The Auditor) du TP "The Refactoring Swarm".
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialise l'agent auditeur.
        
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
            convert_system_message_to_human=True
        )
        print(f" AuditorAgent initialisé avec le modèle : {model_name}")
    
    def analyze(self, target_dir: str) -> Dict:
        """
        Analyse tous les fichiers Python d'un dossier et logue chaque fichier individuellement.
        
        Cette méthode respecte le protocole de logging du TP en enregistrant :
        - file_analyzed : Nom du fichier Python analysé
        - issues_found : Nombre d'erreurs détectées pour ce fichier
        - input_prompt : Le prompt envoyé au LLM (OBLIGATOIRE)
        - output_response : La réponse du LLM (OBLIGATOIRE)
        
        Args:
            target_dir: Chemin du dossier à analyser (ex: "./sandbox/dataset_inconnu")
            
        Returns:
            Dict: Rapport d'audit contenant les problèmes détectés
        """
        print(f"\ [AUDITOR] Démarrage de l'analyse de : {target_dir}")
        
        try:
            
            print(" Recherche des fichiers Python...")
            python_files = list_python_files(target_dir)
            
            if not python_files:
                print("  Aucun fichier Python trouvé dans le dossier.")
                
                
                log_experiment(
                    agent_name="Auditor_Agent",
                    model_used=self.model_name,
                    action=ActionType.ANALYSIS,
                    details={
                        "file_analyzed": "N/A",
                        "input_prompt": f"Analyse du dossier {target_dir}",
                        "output_response": "Aucun fichier Python trouvé dans le dossier cible",
                        "issues_found": 0,
                        "target_directory": target_dir
                    },
                    status="SUCCESS"
                )
                
                return {
                    "files_analyzed": [],
                    "total_issues": 0,
                    "issues": [],
                    "recommendations": ["Aucun fichier Python à analyser"]
                }
            
            print(f" {len(python_files)} fichier(s) Python trouvé(s)")
            
            
            all_issues = []
            files_analyzed = []
            
            for filename in python_files:
                print(f"\n Analyse de : {filename}")
                
                try:
                    
                    full_path = os.path.join(target_dir, filename)
                    file_content = read_file_safe(full_path, target_dir)
                    
                    
                    print(f"   Exécution de pylint sur {filename}...")
                    pylint_output = run_pylint(full_path)
                    pylint_result = parse_pylint_output(pylint_output)
                    pylint_score = pylint_result.get("score", 0)
                    pylint_issues = pylint_result.get("issues", [])
                    
                    print(f"   Score Pylint : {pylint_score}/10")
                    print(f"   Problèmes Pylint détectés : {len(pylint_issues)}")
                    
                    
                    user_prompt = self._build_analysis_prompt(
                        filename=filename,
                        file_content=file_content,
                        pylint_result=pylint_result
                    )
                    
                    
                    print(f"   Consultation du LLM pour l'analyse approfondie...")
                    llm_response = self._call_llm(user_prompt)
                    
                    
                    file_issues = self._parse_llm_response(llm_response, filename)
                    file_issues_count = len(file_issues)
                    
                    
                    log_experiment(
                        agent_name="Auditor_Agent",
                        model_used=self.model_name,
                        action=ActionType.ANALYSIS,
                        details={
                            "file_analyzed": filename,  
                            "input_prompt": user_prompt,  
                            "output_response": llm_response,  
                            "issues_found": file_issues_count,  
                            "pylint_score": pylint_score,
                            "pylint_issues_count": len(pylint_issues),
                            "file_path": full_path,
                            
                        },
                        status="SUCCESS"  
                    )
                    
                    
                    all_issues.extend(file_issues)
                    files_analyzed.append(filename)
                    
                    print(f"  {'' if file_issues_count == 0 else ''} Analyse terminée : {file_issues_count} problème(s) détecté(s)")
                    
                except Exception as e:
                    print(f" Erreur lors de l'analyse de {filename} : {str(e)}")
                    
                    
                    log_experiment(
                        agent_name="Auditor_Agent",
                        model_used=self.model_name,
                        action=ActionType.DEBUG,
                        details={
                            "file_analyzed": filename,
                            "input_prompt": f"Tentative d'analyse de {filename} dans {target_dir}",
                            "output_response": f" Erreur : {str(e)}",
                            "issues_found": 1,
                            "error_type": type(e).__name__
                        },
                        status="FAILURE"  
                    )
                    
                    
                    all_issues.append({
                        "file": filename,
                        "line": 0,
                        "severity": "high",
                        "type": "analysis_error",
                        "message": f"Erreur lors de l'analyse : {str(e)}"
                    })
            
            
            report = {
                "files_analyzed": files_analyzed,
                "total_issues": len(all_issues),
                "issues": all_issues,
                "recommendations": self._generate_recommendations(all_issues)
            }
            
            print(f"\n [AUDITOR] Analyse terminée : {report['total_issues']} problème(s) au total")
            
            return report
            
        except Exception as e:
            print(f" [AUDITOR] Erreur critique lors de l'analyse : {str(e)}")
            
            
            log_experiment(
                agent_name="Auditor_Agent",
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "file_analyzed": "system_error",
                    "input_prompt": f"Analyse du dossier {target_dir}",
                    "output_response": f" Erreur système : {str(e)}",
                    "issues_found": 1,
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            raise
    
    def _build_analysis_prompt(self, filename: str, file_content: str, 
                               pylint_result: Dict) -> str:
        """
        Construit le prompt pour l'analyse d'un fichier.
        
        Args:
            filename: Nom du fichier
            file_content: Contenu du fichier
            pylint_result: Résultat de l'analyse pylint
            
        Returns:
            str: Prompt formaté pour le LLM
        """
        pylint_issues = pylint_result.get('issues', [])
        issues_summary = pylint_issues[:10] if len(pylint_issues) > 10 else pylint_issues
        
        return f"""Analyse ce code Python et le rapport pylint pour identifier les problèmes de qualité.

FICHIER : {filename}
SCORE PYLINT : {pylint_result.get('score', 0)}/10
NOMBRE D'ERREURS PYLINT : {len(pylint_issues)}

CODE :
```python
{file_content[:2000]}{"..." if len(file_content) > 2000 else ""}
```

ERREURS PYLINT (échantillon des plus importantes) :
{issues_summary}

INSTRUCTIONS :
1. Identifie les problèmes les plus critiques (bugs, erreurs de logique, code non maintenable)
2. Classe-les par sévérité : "high", "medium", "low"
3. Propose des recommandations concrètes

Génère un rapport JSON strict avec les champs : files_analyzed, total_issues, issues, recommendations.
Réponds UNIQUEMENT avec du JSON valide."""
    
    def _call_llm(self, prompt: str) -> str:
        """
        Appelle le LLM avec le prompt système et le prompt utilisateur.
        
        Args:
            prompt: Prompt utilisateur
            
        Returns:
            str: Réponse du LLM
        """
        messages = [
            {"role": "system", "content": AUDITOR_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.invoke(messages)
        
        
        if isinstance(response.content, list):
            content = response.content[0] if response.content else ""
            if hasattr(content, 'text'):
                return content.text
            return str(content)
        
        return response.content
    
    def _parse_llm_response(self, response: str, filename: str) -> List[Dict]:
        """
        Parse la réponse JSON du LLM.
        
        Args:
            response: Réponse brute du LLM
            filename: Nom du fichier analysé
            
        Returns:
            List[Dict]: Liste des problèmes détectés
        """
        import json
        
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
            issues = data.get("issues", [])
            
            
            for issue in issues:
                if "file" not in issue:
                    issue["file"] = filename
            
            return issues
            
        except json.JSONDecodeError as e:
            print(f"  Impossible de parser la réponse JSON du LLM : {str(e)}")
            print(f"Réponse brute : {response[:200]}...")
            
            
            return [{
                "file": filename,
                "line": 0,
                "severity": "medium",
                "type": "parse_error",
                "message": "Erreur lors de l'analyse LLM - Réponse non valide"
            }]
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """
        Génère des recommandations basées sur les problèmes détectés.
        
        Args:
            issues: Liste des problèmes
            
        Returns:
            List[str]: Recommandations
        """
        if not issues:
            return [" Le code semble conforme aux standards Python"]
        
        recommendations = []
        issue_types = set(issue.get("type", "") for issue in issues)
        
        
        if "missing_docstring" in issue_types:
            recommendations.append(" Ajouter des docstrings aux fonctions et classes")
        if "syntax_error" in issue_types:
            recommendations.append(" Corriger les erreurs de syntaxe")
        if "naming_convention" in issue_types:
            recommendations.append(" Respecter les conventions de nommage PEP8")
        if "import_error" in issue_types:
            recommendations.append(" Vérifier et corriger les imports")
        if "unused_variable" in issue_types:
            recommendations.append(" Supprimer les variables non utilisées")
        if "complexity" in issue_types:
            recommendations.append(" Réduire la complexité cyclomatique des fonctions")
        if "security" in issue_types:
            recommendations.append(" Corriger les vulnérabilités de sécurité")
        if "type_error" in issue_types:
            recommendations.append(" Corriger les erreurs de typage")
        if "logic_error" in issue_types:
            recommendations.append(" Corriger les erreurs de logique")
        
        
        high_severity_count = sum(1 for issue in issues if issue.get("severity") == "high")
        medium_severity_count = sum(1 for issue in issues if issue.get("severity") == "medium")
        low_severity_count = sum(1 for issue in issues if issue.get("severity") == "low")
        
        if high_severity_count > 0:
            recommendations.insert(0, f" PRIORITÉ : Corriger les {high_severity_count} problème(s) de sévérité HAUTE")
        
        if medium_severity_count > 3:
            recommendations.append(f" Attention : {medium_severity_count} problème(s) de sévérité moyenne à traiter")
        
        if low_severity_count > 5:
            recommendations.append(f" {low_severity_count} problème(s) mineurs identifiés")
            
        return recommendations if recommendations else [" Améliorer la qualité générale du code"]
