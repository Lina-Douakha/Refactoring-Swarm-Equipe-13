"""
Agent Correcteur (The Fixer)
Rôle : Corriger le code Python selon le rapport d'audit ET générer du nouveau contenu.
"""

import os
from dotenv import load_dotenv 
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.logger import log_experiment, ActionType

load_dotenv()

from src.tools.file_tools import read_file_safe, write_file_safe

try:
    from src.prompts.fixer_prompts import FIXER_SYSTEM_PROMPT
except ImportError:
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
    Agent responsable de la correction du code et de la génération de contenu.
    Applique les corrections basées sur le rapport d'audit ET peut créer des tests/documentation.
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialise l'agent correcteur.
        
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
            temperature=0.2,
            convert_system_message_to_human=True 
        )
        print(f" FixerAgent initialisé avec le modèle : {model_name}")
    
    def fix(self, audit_report: Dict, target_dir: str) -> Dict:
        """
        Corrige les fichiers selon le rapport d'audit (ActionType.FIX).
        
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
            
            
            issues_by_file = self._group_issues_by_file(issues)
            
            files_fixed = []
            total_fixes = 0
            
            
            for filename, file_issues in issues_by_file.items():
                print(f"\n Correction de : {filename}")
                
                filepath = os.path.join(target_dir, filename)
                
                try:
                    original_content = read_file_safe(filepath, target_dir)
                except Exception as e:
                    print(f"  Impossible de lire {filename} : {str(e)}")
                    continue
                
                
                user_prompt = self._build_fix_prompt(
                    filename=filename,
                    original_content=original_content,
                    issues=file_issues
                )
                
                
                print(f"   Génération du code corrigé...")
                fixed_content = self._call_llm(user_prompt)
                fixed_content = self._clean_code_response(fixed_content)
                
                
                try:
                    write_file_safe(filepath, fixed_content, target_dir)
                    print(f"   Fichier corrigé et sauvegardé")
                    files_fixed.append(filename)
                    total_fixes += len(file_issues)
                except Exception as e:
                    print(f"   Erreur lors de l'écriture de {filename} : {str(e)}")
                    continue
                
                
                log_experiment(
                    agent_name="Fixer_Agent",
                    model_used=self.model_name,
                    action=ActionType.FIX,  
                    details={
                        "file_analyzed": filename,
                        "input_prompt": user_prompt,
                        "output_response": fixed_content[:500] + "..." if len(fixed_content) > 500 else fixed_content,
                        "issues_found": len(file_issues),  
                        "issues_types": [issue.get("type") for issue in file_issues]
                    },
                    status="SUCCESS"
                )
            
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
                    "file_analyzed": "system_error",
                    "input_prompt": f"Correction des fichiers dans {target_dir}",
                    "output_response": f"Erreur : {str(e)}",
                    "issues_found": 1,
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            raise
    
    def generate_tests(self, filename: str, target_dir: str) -> str:
        """
        Génère des tests unitaires pour un fichier (ActionType.GENERATION).
        CRÉE un NOUVEAU fichier qui n'existait pas.
        
        Args:
            filename: Nom du fichier source
            target_dir: Dossier cible
            
        Returns:
            str: Contenu des tests générés
        """
        print(f"\n [FIXER] Génération de tests pour : {filename}")
        
        try:
            filepath = os.path.join(target_dir, filename)
            code_content = read_file_safe(filepath, target_dir)
            
            
            prompt = f"""Génère des tests unitaires pytest pour ce code Python :

FICHIER : {filename}

CODE :
```python
{code_content}
```

INSTRUCTIONS :
1. Crée au moins 5 tests unitaires complets
2. Utilise pytest et les fixtures si nécessaire
3. Teste les cas normaux ET les cas d'erreur
4. Nomme les tests de façon explicite (test_nom_fonction_cas)
5. Ajoute des docstrings aux tests
6. Import toutes les dépendances nécessaires

Retourne UNIQUEMENT le code des tests, sans explication."""
            
            
            test_content = self._call_llm(prompt)
            test_content = self._clean_code_response(test_content)
            
            
            test_filename = f"test_{filename}"
            test_filepath = os.path.join(target_dir, test_filename)
            write_file_safe(test_filepath, test_content, target_dir)
            
            
            log_experiment(
                agent_name="Fixer_Agent",
                model_used=self.model_name,
                action=ActionType.GENERATION,  
                details={
                    "file_analyzed": test_filename,  
                    "input_prompt": prompt,
                    "output_response": test_content[:500] + "..." if len(test_content) > 500 else test_content,
                    "issues_found": 0,  
                    "source_file": filename,
                    "content_type": "unit_tests"
                },
                status="SUCCESS"
            )
            
            print(f" Tests générés : {test_filename}")
            return test_content
            
        except Exception as e:
            print(f" Erreur lors de la génération de tests : {str(e)}")
            
            log_experiment(
                agent_name="Fixer_Agent",
                model_used=self.model_name,
                action=ActionType.GENERATION,
                details={
                    "file_analyzed": f"test_{filename}",
                    "input_prompt": f"Génération de tests pour {filename}",
                    "output_response": f"Erreur : {str(e)}",
                    "issues_found": 1,
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            raise
    
    def generate_documentation(self, filename: str, target_dir: str) -> str:
        """
        Génère de la documentation pour un fichier (ActionType.GENERATION).
        CRÉE un NOUVEAU fichier de documentation.
        
        Args:
            filename: Nom du fichier source
            target_dir: Dossier cible
            
        Returns:
            str: Contenu de la documentation
        """
        print(f"\n [FIXER] Génération de documentation pour : {filename}")
        
        try:
            filepath = os.path.join(target_dir, filename)
            code_content = read_file_safe(filepath, target_dir)
            
            prompt = f"""Génère une documentation complète pour ce code Python :

FICHIER : {filename}

CODE :
```python
{code_content}
```

INSTRUCTIONS :
Crée un README.md avec :
1. 
   - Résumé du module/fichier
   - Objectif principal

2. 
   - Liste des fonctions avec description
   - Paramètres et retours

3. 
   - Exemples de code concrets
   - Cas d'usage typiques

4. 
   - Liste des imports nécessaires

Format Markdown strict. Sois concis mais complet."""
            
            doc_content = self._call_llm(prompt)
            
            
            doc_filename = f"README_{filename.replace('.py', '')}.md"
            doc_filepath = os.path.join(target_dir, doc_filename)
            write_file_safe(doc_filepath, doc_content, target_dir)
            
            
            log_experiment(
                agent_name="Fixer_Agent",
                model_used=self.model_name,
                action=ActionType.GENERATION,
                details={
                    "file_analyzed": doc_filename,
                    "input_prompt": prompt,
                    "output_response": doc_content[:500] + "..." if len(doc_content) > 500 else doc_content,
                    "issues_found": 0,
                    "source_file": filename,
                    "content_type": "documentation"
                },
                status="SUCCESS"
            )
            
            print(f" Documentation générée : {doc_filename}")
            return doc_content
            
        except Exception as e:
            print(f" Erreur lors de la génération de documentation : {str(e)}")
            
            log_experiment(
                agent_name="Fixer_Agent",
                model_used=self.model_name,
                action=ActionType.GENERATION,
                details={
                    "file_analyzed": f"README_{filename.replace('.py', '')}.md",
                    "input_prompt": f"Génération de documentation pour {filename}",
                    "output_response": f"Erreur : {str(e)}",
                    "issues_found": 1,
                    "error_type": type(e).__name__
                },
                status="FAILURE"
            )
            raise
    
    def retry_fix(self, filepath: str, target_dir: str, error_message: str) -> str:
        """
        Réessaye de corriger un fichier suite à une erreur (ActionType.FIX).
        
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
                    "file_analyzed": os.path.basename(filepath),
                    "input_prompt": retry_prompt,
                    "output_response": fixed_content[:500] + "..." if len(fixed_content) > 500 else fixed_content,
                    "issues_found": 1,  
                    "retry": True,
                    "error_message": error_message[:200]
                },
                status="SUCCESS"
            )
            
            print(f" Nouvelle version générée")
            return fixed_content
            
        except Exception as e:
            print(f" Échec de la nouvelle tentative : {str(e)}")
            
            log_experiment(
                agent_name="Fixer_Agent",
                model_used=self.model_name,
                action=ActionType.FIX,
                details={
                    "file_analyzed": os.path.basename(filepath),
                    "input_prompt": f"Retry fix pour {os.path.basename(filepath)}",
                    "output_response": f"Erreur : {str(e)}",
                    "issues_found": 1,
                    "retry": True
                },
                status="FAILURE"
            )
            raise
    
    def _group_issues_by_file(self, issues: List[Dict]) -> Dict[str, List[Dict]]:
        """Regroupe les problèmes par fichier."""
        grouped = {}
        for issue in issues:
            filename = issue.get("file", "unknown.py")
            if filename not in grouped:
                grouped[filename] = []
            grouped[filename].append(issue)
        return grouped
    
    def _build_fix_prompt(self, filename: str, original_content: str, 
                          issues: List[Dict]) -> str:
        """Construit le prompt pour corriger un fichier."""
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
        """Appelle le LLM."""
        messages = [
            {"role": "system", "content": FIXER_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        response = self.llm.invoke(messages)
        
        if isinstance(response.content, list):
            content = response.content[0] if response.content else ""
            if hasattr(content, 'text'):
                return content.text
            return str(content)
        
        return response.content
    
    def _clean_code_response(self, response: str) -> str:
        """Nettoie la réponse du LLM (enlève les balises markdown)."""
        cleaned = response.strip()
        
        if cleaned.startswith("```python"):
            cleaned = cleaned[9:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
