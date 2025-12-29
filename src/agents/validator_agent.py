
from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.utils.code_utils import is_valid_python, get_syntax_errors

class ValidatorAgent(BaseAgent):
    '''Agent qui valide le code corrigé'''
    
    def __init__(self):
        super().__init__(
            name='Validator',
            role='Code Validation',
            temperature=0.1
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        '''Valide que le code corrigé est correct'''
        self.logger.info('Validation du code corrigé')
        
        corrected_code = state.get('corrected_code', '')
        original_code = state.get('code', '')
        
        validation = {
            'is_valid_syntax': is_valid_python(corrected_code),
            'syntax_errors': get_syntax_errors(corrected_code),
            'approved': False
        }
        
        # Validation par LLM
        prompt = f'''Compare le code original et le code corrigé:

CODE ORIGINAL:
```python
{original_code}
```

CODE CORRIGÉ:
```python
{corrected_code}
```

Questions:
1. Le code corrigé est-il syntaxiquement valide?
2. Tous les bugs ont-ils été corrigés?
3. La fonctionnalité est-elle préservée?
4. Y a-t-il de nouvelles erreurs introduites?

Réponds par OUI ou NON suivi d'une explication brève.
'''
        
        try:
            llm_response = self.invoke_llm(prompt)
            validation['llm_validation'] = llm_response
            
            # Décision d'approbation
            if validation['is_valid_syntax'] and 'OUI' in llm_response.upper():
                validation['approved'] = True
                self.logger.info('✅ Code validé et approuvé')
            else:
                self.logger.warning('❌ Code non approuvé')
                
        except Exception as e:
            self.logger.error(f'Erreur validation: {e}')
            validation['llm_validation'] = str(e)
        
        state['validation'] = validation
        state['current_step'] = 'validated'
        
        return state