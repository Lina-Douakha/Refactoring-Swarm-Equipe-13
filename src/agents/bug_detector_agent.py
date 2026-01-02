from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.utils.language_detector import validate_syntax_with_llm

class BugDetectorAgent(BaseAgent):
    """Agent specialise dans la detection de bugs TOUS LANGAGES"""
    
    def __init__(self):
        super().__init__(
            name='BugDetector',
            role='Multi-Language Bug Detection',
            temperature=0.1
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Detecte les bugs dans n'importe quel langage"""
        self.logger.info(' Detection de bugs multi-langages en cours')
        
        code = state.get('code', '')
        detected_language = state.get('detected_language', 'unknown')
        
        if not code:
            self.logger.warning(' Aucun code à analyser')
            state['bugs'] = {'error': 'Pas de code fourni'}
            return state
        
        self.logger.info(f' Analyse du code {detected_language}')
        
        # 1. VALIDATION SYNTAXE via LLM
        syntax_validation = validate_syntax_with_llm(code, detected_language)
        
        bugs = {
            'language': detected_language,
            'syntax_validation': syntax_validation,
            'detected_bugs': []
        }
        
        # 2. DeTECTION APPROFONDIE PAR LLM (100% dynamique)
        prompt = f"""Tu es un expert en detection de bugs pour {detected_language}.

CODE À ANALYSER:
```{detected_language}
{code}
```

MISSION: Trouve TOUS les bugs possibles.

Pour CHAQUE bug detecte, fournis:
1. **Type**: syntaxe / logique / runtime / securite / performance
2. **Ligne**: numero de ligne approximatif
3. **Description**: explication claire du problème
4. **Gravite**: critique / importante / mineure
5. **Solution**: comment corriger

Reponds en JSON structure:
{{
    "bugs": [
        {{
            "type": "...",
            "line": 10,
            "description": "...",
            "severity": "critique",
            "fix_suggestion": "..."
        }}
    ],
    "total_bugs": 0,
    "code_health": "healthy/needs_attention/critical"
}}
"""
        
        try:
            llm_response = self.invoke_llm(prompt)
            bugs['llm_detected'] = llm_response
            self.logger.info(f' Bugs detectes pour {detected_language}')
        except Exception as e:
            self.logger.error(f' Erreur detection: {e}')
            bugs['llm_detected'] = str(e)
        
        state['bugs'] = bugs
        state['current_step'] = 'bugs_detected'
        
        return state