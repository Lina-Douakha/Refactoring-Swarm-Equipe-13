from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.utils.code_utils import count_lines
from src.utils.language_detector import detect_language_with_llm

class AnalyzerAgent(BaseAgent):
    """Agent qui analyse le code TOUS LANGAGES"""
    
    def __init__(self):
        super().__init__(
            name='Analyzer',
            role='Multi-Language Code Analysis',
            temperature=0.2
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse le code et identifie les zones problématiques"""
        self.logger.info('🔍 Début de l\'analyse multi-langages')
        
        code = state.get('code', '')
        filename = state.get('filename', '')
        
        if not code:
            self.logger.warning('⚠️ Aucun code à analyser')
            state['analysis'] = {'error': 'Pas de code fourni'}
            return state
        
        # 1. DÉTECTION DU LANGAGE via LLM
        self.logger.info('🤖 Détection du langage via LLM...')
        lang_detection = detect_language_with_llm(code, filename)
        
        # ✅ EXTRAIRE PROPREMENT le langage
        detected_language = lang_detection.get('language', 'unknown')
        
        self.logger.info(f'✅ Langage détecté: {detected_language}')
        
        # 2. ANALYSE BASIQUE
        analysis = {
            'detected_language': detected_language,
            'language_detection_details': lang_detection,
            'lines_count': count_lines(code),
            'issues': []
        }
        
        # 3. ANALYSE PAR LLM (prompt COURT)
        prompt = f"""Analyse ce code {detected_language}.

CODE:
```
{code[:500]}
```

Liste les bugs principaux en 3-4 lignes maximum.
"""
        
        try:
            llm_response = self.invoke_llm(prompt)
            analysis['llm_analysis'] = llm_response
            self.logger.info('✅ Analyse LLM complétée')
        except Exception as e:
            self.logger.error(f'❌ Erreur analyse LLM: {e}')
            analysis['llm_analysis'] = f'Erreur: {str(e)}'
        
        # ✅ METTRE À JOUR L'ÉTAT AVEC LE LANGAGE
        state['analysis'] = analysis
        state['detected_language'] = detected_language  # ✅ IMPORTANT!
        state['current_step'] = 'analyzed'
        
        return state