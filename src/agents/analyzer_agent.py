
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.utils.code_utils import count_lines, is_valid_python

class AnalyzerAgent(BaseAgent):
    '''Agent qui analyse le code pour identifier les problèmes'''
    
    def __init__(self):
        super().__init__(
            name='Analyzer',
            role='Code Analysis',
            temperature=0.2
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        '''Analyse le code et identifie les zones problématiques'''
        self.logger.info('Début de l\'analyse du code')
        
        code = state.get('code', '')
        
        if not code:
            self.logger.warning('Aucun code à analyser')
            state['analysis'] = {'error': 'Pas de code fourni'}
            return state
        
        # Analyse basique
        analysis = {
            'lines_count': count_lines(code),
            'is_valid_syntax': is_valid_python(code),
            'issues': []
        }
        
        # Analyse par LLM
        prompt = f'''Analyse ce code Python et identifie les problèmes potentiels:
```python
{code}
```

Liste les problèmes en JSON format:
{{
    "syntax_errors": [],
    "logic_errors": [],
    "code_smells": [],
    "security_issues": []
}}
'''
        
        try:
            llm_response = self.invoke_llm(prompt)
            analysis['llm_analysis'] = llm_response
            self.logger.info('Analyse complétée')
        except Exception as e:
            self.logger.error(f'Erreur lors de l\'analyse LLM: {e}')
            analysis['llm_analysis'] = str(e)
        
        state['analysis'] = analysis
        state['current_step'] = 'analyzed'
        
        return state