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

# Import des outils du Toolsmith
from src.tools.file_tools import read_file_safe, list_python_files
from src.tools.pylint_tool import run_pylint, parse_pylint_output

# Import du prompt système
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
            model_name: Nom du modèle LLM à utiliser (défaut: gemini-1.5-flash)
        """
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1,  # Basse température pour plus de précision
            convert_system_message_to_human=True
        )
        print(f"✅ AuditorAgent initialisé avec le modèle : {model_name}")
    
    def analyze(self, target_dir: str) -> Dict:
        """
        Analyse tous les fichiers Python d'un dossier.
        
        Args:
            target_dir: Chemin du dossier à analyser
            
        Returns:
            Dict: Rapport d'audit contenant les problèmes détectés
        """
        print(f"\n🔍 [AUDITOR] Démarrage de l'analyse de : {target_dir}")
        
        try:
            # Étape 1 : Lister les fichiers Python
            print("📂 Recherche des fichiers Python...")
            python_files = list_python_files(target_dir)
            
            if not python_files:
                print("⚠️  Aucun fichier Python trouvé dans le dossier.")
                return {
                    "files_analyzed": [],
                    "total_issues": 0,
                    "issues": [],
                    "recommendations": ["Aucun fichier Python à analyser"]
                }
            
            print(f"✅ {len(python_files)} fichier(s) Python trouvé(s)")
            
            # Étape 2 : Analyser chaque fichier
            all_issues = []
            files_analyzed = []
            
            for filename in python_files:
                print(f"\n📄 Analyse de : {filename}")
                
                # Construire le chemin complet
                full_path = os.path.join(target_dir, filename)
                
                # Lire le contenu du fichier
                file_content = read_file_safe(full_path, target_dir)  
                
                # Lancer pylint et parser le résultat
                pylint_output = run_pylint(full_path)
                pylint_result = parse_pylint_output(pylint_output)
                
                # Construire le prompt pour le LLM
                user_prompt = self._build_analysis_prompt(
                    filename=filename,
                    file_content=file_content,
                    pylint_result=pylint_result
                )
                
                # Appeler le LLM
                print(f"🤖 Consultation du LLM pour l'analyse...")
                llm_response = self._call_llm(user_prompt)
                
                # Logger l'interaction
                log_experiment(
                    agent_name="Auditor_Agent",
                    model_used=self.model_name,
                    action=ActionType.ANALYSIS,
                    details={
                        "file_analyzed": filename,
                        "pylint_score": pylint_result.get("score", 0),
                        "input_prompt": user_prompt,
                        "output_response": llm_response,
                    },
                    status="SUCCESS"
                )
                
                # Parser la réponse du LLM
                file_issues = self._parse_llm_response(llm_response, filename)
                all_issues.extend(file_issues)
                files_analyzed.append(filename)
                
                print(f"✅ Analyse terminée : {len(file_issues)} problème(s) détecté(s)")
            
            # Étape 3 : Générer le rapport final
            report = {
                "files_analyzed": files_analyzed,
                "total_issues": len(all_issues),
                "issues": all_issues,
                "recommendations": self._generate_recommendations(all_issues)
            }
            
            print(f"\n✅ [AUDITOR] Analyse terminée : {report['total_issues']} problème(s) au total")
            return report
            
        except Exception as e:
            print(f"❌ [AUDITOR] Erreur lors de l'analyse : {str(e)}")
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
        # Limiter les issues pylint pour ne pas surcharger le prompt
        pylint_issues = pylint_result.get('issues', [])
        issues_summary = pylint_issues[:10] if len(pylint_issues) > 10 else pylint_issues
        
        return f"""Analyse ce code Python et le rapport pylint.

FICHIER : {filename}
SCORE PYLINT : {pylint_result.get('score', 0)}/10

CODE :
```python
{file_content}
```

ERREURS PYLINT (échantillon) :
{issues_summary}

Génère un rapport JSON avec les problèmes détectés les plus importants."""
    
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
            issues = data.get("issues", [])
            
            # S'assurer que chaque issue a le nom du fichier
            for issue in issues:
                if "file" not in issue:
                    issue["file"] = filename
            
            return issues
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Impossible de parser la réponse JSON du LLM : {str(e)}")
            # En cas d'échec, créer au moins un issue basique
            return [{
                "file": filename,
                "line": 0,
                "severity": "medium",
                "type": "parse_error",
                "message": "Erreur lors de l'analyse LLM"
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
            return ["Le code semble conforme aux standards Python"]
        
        recommendations = []
        issue_types = set(issue.get("type", "") for issue in issues)
        
        if "missing_docstring" in issue_types:
            recommendations.append("Ajouter des docstrings aux fonctions et classes")
        if "syntax_error" in issue_types:
            recommendations.append("Corriger les erreurs de syntaxe")
        if "naming_convention" in issue_types:
            recommendations.append("Respecter les conventions de nommage PEP8")
        if "import_error" in issue_types:
            recommendations.append("Vérifier les imports")
        if "unused_variable" in issue_types:
            recommendations.append("Supprimer les variables non utilisées")
            
        return recommendations if recommendations else ["Améliorer la qualité générale du code"]