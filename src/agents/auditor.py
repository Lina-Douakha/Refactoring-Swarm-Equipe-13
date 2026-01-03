"""
Agent Auditeur (The Auditor)
Rôle : Analyser le code Python, détecter les problèmes de qualité et générer un rapport.
"""

import os
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.logger import log_experiment, ActionType

# Import des outils du Toolsmith (à créer)
# Ces imports seront décommentés une fois que le Toolsmith aura créé les fichiers
try:
    from src.tools.file_tools import read_file_safe, list_python_files
    from src.tools.pylint_tool import run_pylint
except ImportError:
    print("  ATTENTION : Les outils du Toolsmith ne sont pas encore disponibles.")
    print("   Les fonctions suivantes doivent être créées :")
    print("   - src/tools/file_tools.py : read_file_safe(), list_python_files()")
    print("   - src/tools/pylint_tool.py : run_pylint()")

# Import du prompt système (à créer par le Prompt Engineer)
try:
    from src.prompts.auditor_prompts import AUDITOR_SYSTEM_PROMPT
except ImportError:
    # Prompt de secours si le Prompt Engineer n'a pas encore créé le fichier
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
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialise l'agent auditeur.
        
        Args:
            model_name: Nom du modèle LLM à utiliser (défaut: gemini-2.0-flash-exp)
        """
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1,  # Basse température pour plus de précision
        )
        print(f" AuditorAgent initialisé avec le modèle : {model_name}")
    
    def analyze(self, target_dir: str) -> Dict:
        """
        Analyse tous les fichiers Python d'un dossier.
        
        Args:
            target_dir: Chemin du dossier à analyser
            
        Returns:
            Dict: Rapport d'audit contenant les problèmes détectés
        """
        print(f"\n [AUDITOR] Démarrage de l'analyse de : {target_dir}")
        
        try:
            # Étape 1 : Lister les fichiers Python
            print(" Recherche des fichiers Python...")
            python_files = list_python_files(target_dir)
            
            if not python_files:
                print("  Aucun fichier Python trouvé dans le dossier.")
                return {
                    "files_analyzed": [],
                    "total_issues": 0,
                    "issues": [],
                    "recommendations": ["Aucun fichier Python à analyser"]
                }
            
            print(f" {len(python_files)} fichier(s) Python trouvé(s)")
            
            # Étape 2 : Analyser chaque fichier
            all_issues = []
            files_analyzed = []
            
            for filepath in python_files:
                print(f"\n Analyse de : {os.path.basename(filepath)}")
                
                # Lire le contenu du fichier
                file_content = read_file_safe(filepath, target_dir)
                
                # Lancer pylint
                pylint_result = run_pylint(filepath)
                
                # Construire le prompt pour le LLM
                user_prompt = self._build_analysis_prompt(
                    filepath=filepath,
                    file_content=file_content,
                    pylint_result=pylint_result
                )
                
                # Appeler le LLM
                print(f" Consultation du LLM pour l'analyse...")
                llm_response = self._call_llm(user_prompt)
                
                # Logger l'interaction
                log_experiment(
                    agent_name="Auditor_Agent",
                    model_used=self.model_name,
                    action=ActionType.ANALYSIS,
                    details={
                        "file_analyzed": os.path.basename(filepath),
                        "pylint_score": pylint_result.get("score", 0),
                        "input_prompt": user_prompt,
                        "output_response": llm_response,
                    },
                    status="SUCCESS"
                )
                
                # Parser la réponse du LLM
                file_issues = self._parse_llm_response(llm_response)
                all_issues.extend(file_issues)
                files_analyzed.append(os.path.basename(filepath))
                
                print(f" Analyse terminée : {len(file_issues)} problème(s) détecté(s)")
            
            # Étape 3 : Générer le rapport final
            report = {
                "files_analyzed": files_analyzed,
                "total_issues": len(all_issues),
                "issues": all_issues,
                "recommendations": self._generate_recommendations(all_issues)
            }
            
            print(f"\n [AUDITOR] Analyse terminée : {report['total_issues']} problème(s) au total")
            return report
            
        except Exception as e:
            print(f" [AUDITOR] Erreur lors de l'analyse : {str(e)}")
            log_experiment(
                agent_name="Auditor_Agent",
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "input_prompt": f"Analyse du dossier {target_dir}",
                    "output_response": f"Erreur : {str(e)}",
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            raise
    
    def _build_analysis_prompt(self, filepath: str, file_content: str, 
                               pylint_result: Dict) -> str:
        """
        Construit le prompt pour l'analyse d'un fichier.
        
        Args:
            filepath: Chemin du fichier
            file_content: Contenu du fichier
            pylint_result: Résultat de l'analyse pylint
            
        Returns:
            str: Prompt formaté pour le LLM
        """
        return f"""Analyse ce code Python et le rapport pylint.

FICHIER : {os.path.basename(filepath)}
SCORE PYLINT : {pylint_result.get('score', 0)}/10

CODE :
```python
{file_content}
```

ERREURS PYLINT :
{pylint_result.get('issues', [])}

Génère un rapport JSON avec les problèmes détectés."""
    
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
        return response.content
    
    def _parse_llm_response(self, response: str) -> List[Dict]:
        """
        Parse la réponse JSON du LLM.
        
        Args:
            response: Réponse brute du LLM
            
        Returns:
            List[Dict]: Liste des problèmes détectés
        """
        import json
        
        try:
            # Nettoyer la réponse (enlever les balises markdown si présentes)
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            data = json.loads(cleaned)
            return data.get("issues", [])
        except json.JSONDecodeError:
            print("  Impossible de parser la réponse JSON du LLM")
            return []
    
    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """
        Génère des recommandations basées sur les problèmes détectés.
        
        Args:
            issues: Liste des problèmes
            
        Returns:
            List[str]: Recommandations
        """
        if not issues:
            return ["Le code semble conforme aux standards Python"]
        
        recommendations = []
        issue_types = set(issue.get("type", "") for issue in issues)
        
        if "missing_docstring" in issue_types:
            recommendations.append("Ajouter des docstrings aux fonctions et classes")
        if "syntax_error" in issue_types:
            recommendations.append("Corriger les erreurs de syntaxe")
        if "naming_convention" in issue_types:
            recommendations.append("Respecter les conventions de nommage PEP8")
            
        return recommendations if recommendations else ["Améliorer la qualité générale du code"]