
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.utils.code_utils import get_syntax_errors

class BugDetectorAgent(BaseAgent):
    '''Agent spécialisé dans la détection de bugs'''
    
    def __init__(self):
        super().__init__(
            name='BugDetector',
            role='Bug Detection',
            temperature=0.1
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        '''Détecte les bugs dans le code'''
        self.logger.info('Détection de bugs en cours')
        
        code = state.get('code', '')
        
        # Vérification syntaxe
        syntax_error = get_syntax_errors(code)
        
        bugs = {
            'syntax_errors': syntax_error if syntax_error else None,
            'detected_bugs': []
        }
        
        # Détection par LLM
        prompt = f'''Tu es un expert en détection de bugs. Analyse ce code et liste TOUS les bugs:
```python
{code}
```

Pour chaque bug trouvé, donne:
1. Type de bug (syntaxe, logique, runtime, sécurité)
2. Ligne concernée
3. Description du problème
4. Gravité (critique/importante/mineure)

Format de réponse clair et structuré.
'''
        
        try:
            llm_response = self.invoke_llm(prompt)
            bugs['llm_detected'] = llm_response
            self.logger.info(f'Bugs détectés: {llm_response[:100]}...')
        except Exception as e:
            self.logger.error(f'Erreur détection: {e}')
            bugs['llm_detected'] = str(e)
        
        state['bugs'] = bugs
        state['current_step'] = 'bugs_detected'
        
        return state