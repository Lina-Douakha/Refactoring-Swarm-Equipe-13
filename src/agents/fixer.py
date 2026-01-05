"""
Agent Correcteur (The Fixer)
Rôle : Corriger le code Python selon le rapport d'audit.
"""

import os
from dotenv import load_dotenv 
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.logger import log_experiment, ActionType
load_dotenv()
# Import des outils du Toolsmith
# Import des outils du Toolsmith
from src.tools.file_tools import read_file_safe, write_file_safe

# Import du prompt système
try:
    from src.prompts.fixer_prompts import FIXER_SYSTEM_PROMPT
except ImportError:
    # Prompt de secours
    FIXER_SYSTEM_PROMPT = """Tu es un expert Python chargé de corriger du code.

MISSION :
Corrige le code Python selon les problèmes indiqués dans le rapport d'audit.

RÈGLES IMPORTANTES :
1. Ne change PAS la logique métier du code
2. Corrige uniquement les problèmes listés
3. Ajoute les docstrings manquantes
4. Respecte PEP8
5. Conserve tous les noms de fonctions/classes existants
6. Ne supprime aucune fonctionnalité

FORMAT DE SORTIE :
Retourne UNIQUEMENT le code Python corrigé, sans explication ni commentaire.
Ne mets pas de balises ```python, juste le code brut."""


class FixerAgent:
    """
    Agent responsable de la correction du code.
    Applique les corrections basées sur le rapport d'audit.
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialise l'agent correcteur.
        
        Args:
            model_name: Nom du modèle LLM à utiliser
        """
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.2,  
        )
        print(f" FixerAgent initialisé avec le modèle : {model_name}")
    
    def fix(self, audit_report: Dict, target_dir: str) -> Dict:
        """
        Corrige les fichiers selon le rapport d'audit.
        
        Args:
            audit_report: Rapport généré par l'Auditor
            target_dir: Dossier contenant les fichiers à corriger
            
        Returns:
            Dict: Résumé des corrections effectuées
        """
        print(f"\n [FIXER] Démarrage des corrections...")
        
        try:
            issues = audit_report.get("issues", [])
            
            if not issues:
                print(" Aucun problème à corriger.")
                return {
                    "files_fixed": [],
                    "total_fixes": 0,
                    "status": "no_issues"
                }
            
            print(f" {len(issues)} problème(s) à corriger")
            
            # Regrouper les problèmes par fichier
            issues_by_file = self._group_issues_by_file(issues)
            
            files_fixed = []
            total_fixes = 0
            
            # Corriger chaque fichier
            for filename, file_issues in issues_by_file.items():
                print(f"\n Correction de : {filename}")
                
                filepath = os.path.join(target_dir, filename)
                
                # Lire le contenu actuel
                try:
                    original_content = read_file_safe(filepath, target_dir)
                except Exception as e:
                    print(f"  Impossible de lire {filename} : {str(e)}")
                    continue
                
                # Construire le prompt de correction
                user_prompt = self._build_fix_prompt(
                    filename=filename,
                    original_content=original_content,
                    issues=file_issues
                )
                
                # Appeler le LLM pour corriger
                print(f" Génération du code corrigé...")
                fixed_content = self._call_llm(user_prompt)
                
                # Nettoyer la réponse (enlever les balises markdown si présentes)
                fixed_content = self._clean_code_response(fixed_content)
                
                # Écrire le code corrigé
                try:
                    write_file_safe(filepath, fixed_content, target_dir)
                    print(f" Fichier corrigé et sauvegardé")
                    files_fixed.append(filename)
                    total_fixes += len(file_issues)
                except Exception as e:
                    print(f" Erreur lors de l'écriture de {filename} : {str(e)}")
                    continue
                
                # Logger la correction
                log_experiment(
                    agent_name="Fixer_Agent",
                    model_used=self.model_name,
                    action=ActionType.FIX,
                    details={
                        "file_fixed": filename,
                        "issues_count": len(file_issues),
                        "input_prompt": user_prompt,
                        "output_response": fixed_content[:500] + "..." if len(fixed_content) > 500 else fixed_content,
                        "issues_types": [issue.get("type") for issue in file_issues]
                    },
                    status="SUCCESS"
                )
            
            # Résumé final
            result = {
                "files_fixed": files_fixed,
                "total_fixes": total_fixes,
                "status": "completed"
            }
            
            print(f"\n [FIXER] Corrections terminées : {total_fixes} problème(s) corrigé(s) dans {len(files_fixed)} fichier(s)")
            return result
            
        except Exception as e:
            print(f" [FIXER] Erreur lors des corrections : {str(e)}")
            log_experiment(
                agent_name="Fixer_Agent",
                model_used=self.model_name,
                action=ActionType.DEBUG,
                details={
                    "input_prompt": f"Correction des fichiers dans {target_dir}",
                    "output_response": f"Erreur : {str(e)}",
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            raise
    
    def _group_issues_by_file(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Regroupe les problèmes par fichier.
        
        Args:
            issues: Liste de tous les problèmes
            
        Returns:
            Dict: Problèmes groupés par nom de fichier
        """
        grouped = {}
        for issue in issues:
            filename = issue.get("file", "unknown.py")
            if filename not in grouped:
                grouped[filename] = []
            grouped[filename].append(issue)
        return grouped
    
    def _build_fix_prompt(self, filename: str, original_content: str, 
                          issues: List[Dict]) -> str:
        """
        Construit le prompt pour corriger un fichier.
        
        Args:
            filename: Nom du fichier
            original_content: Contenu actuel du fichier
            issues: Liste des problèmes à corriger
            
        Returns:
            str: Prompt formaté pour le LLM
        """
        issues_text = "\n".join([
            f"- Ligne {issue.get('line', '?')} : {issue.get('message', 'Problème non spécifié')} "
            f"(Type: {issue.get('type', 'unknown')}, Sévérité: {issue.get('severity', 'medium')})"
            for issue in issues
        ])
        
        return f"""Corrige ce code Python selon les problèmes détectés.

FICHIER : {filename}
NOMBRE DE PROBLÈMES : {len(issues)}

PROBLÈMES À CORRIGER :
{issues_text}

CODE ACTUEL :
```python
{original_content}
```

INSTRUCTIONS :
1. Corrige tous les problèmes listés
2. Ajoute les docstrings manquantes (format Google/NumPy style)
3. Respecte PEP8 (espaces, nommage, etc.)
4. Ne change PAS la logique du code
5. Conserve tous les noms de fonctions/variables

Retourne uniquement le code Python corrigé, sans explication."""
    
    def _call_llm(self, prompt: str) -> str:
        """
        Appelle le LLM pour générer le code corrigé.
        
        Args:
            prompt: Prompt utilisateur
            
        Returns:
            str: Code corrigé généré par le LLM
        """
        messages = [
            {"role": "system", "content": FIXER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def _clean_code_response(self, response: str) -> str:
        """
        Nettoie la réponse du LLM (enlève les balises markdown).
        
        Args:
            response: Réponse brute du LLM
            
        Returns:
            str: Code Python propre
        """
        cleaned = response.strip()
        
        # Enlever les balises markdown
        if cleaned.startswith("```python"):
            cleaned = cleaned[9:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
    
    def retry_fix(self, filepath: str, target_dir: str, error_message: str) -> str:
        """
        Réessaye de corriger un fichier suite à une erreur.
        
        Args:
            filepath: Chemin du fichier
            target_dir: Dossier cible
            error_message: Message d'erreur du test précédent
            
        Returns:
            str: Code corrigé
        """
        print(f"\n [FIXER] Nouvelle tentative de correction pour : {os.path.basename(filepath)}")
        
        try:
            original_content = read_file_safe(filepath, target_dir)
            
            retry_prompt = f"""Le code précédent a échoué aux tests.

FICHIER : {os.path.basename(filepath)}
ERREUR RENCONTRÉE :
{error_message}

CODE ACTUEL :
```python
{original_content}
```

Analyse l'erreur et corrige le code. Retourne uniquement le code Python corrigé."""
            
            fixed_content = self._call_llm(retry_prompt)
            fixed_content = self._clean_code_response(fixed_content)
            
            write_file_safe(filepath, fixed_content, target_dir)
            
            log_experiment(
                agent_name="Fixer_Agent",
                model_used=self.model_name,
                action=ActionType.FIX,
                details={
                    "file_fixed": os.path.basename(filepath),
                    "retry": True,
                    "error_message": error_message,
                    "input_prompt": retry_prompt,
                    "output_response": fixed_content[:500] + "..." if len(fixed_content) > 500 else fixed_content
                },
                status="SUCCESS"
            )
            
            print(f" Nouvelle version générée")
            return fixed_content
            
        except Exception as e:
            print(f" Échec de la nouvelle tentative : {str(e)}")
            raise