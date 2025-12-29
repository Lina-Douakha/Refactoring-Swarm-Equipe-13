
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.utils.code_utils import extract_code_blocks

class RefactorAgent(BaseAgent):
    '''Agent qui corrige et refactorise le code'''
    
    def __init__(self):
        super().__init__(
            name='Refactor',
            role='Code Refactoring',
            temperature=0.3
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        '''Corrige le code bugué'''
        self.logger.info('Refactoring du code')
        
        code = state.get('code', '')
        bugs = state.get('bugs', {})
        analysis = state.get('analysis', {})
        
        prompt = f'''Tu es un expert en refactoring de code Python.

Code original:
```python
{code}
```

Bugs détectés:
{bugs.get('llm_detected', 'Aucun')}

Analyse:
{analysis.get('llm_analysis', 'Aucune')}

TÂCHE: Corrige TOUS les bugs et améliore le code.

Réponds UNIQUEMENT avec le code corrigé entre triple backticks python.
Pas d'explications, juste le code.
'''
        
        try:
            llm_response = self.invoke_llm(prompt)
            
            # Extraire le code corrigé
            code_blocks = extract_code_blocks(llm_response)
            
            if code_blocks:
                corrected_code = code_blocks[0]
                state['corrected_code'] = corrected_code
                self.logger.info('Code corrigé avec succès')
            else:
                state['corrected_code'] = llm_response
                self.logger.warning('Pas de bloc de code trouvé, utilisation de la réponse brute')
                
        except Exception as e:
            self.logger.error(f'Erreur refactoring: {e}')
            state['corrected_code'] = code  # Garde le code original en cas d'erreur
            state['refactor_error'] = str(e)
        
        state['current_step'] = 'refactored'
        
        return state