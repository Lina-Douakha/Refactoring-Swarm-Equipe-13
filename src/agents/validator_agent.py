from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.utils.language_detector import validate_syntax_with_llm

class ValidatorAgent(BaseAgent):
    """Agent qui valide le code corrige TOUS LANGAGES"""
    
    def __init__(self):
        super().__init__(
            name='Validator',
            role='Multi-Language Code Validation',
            temperature=0.1
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Valide que le code corrige est correct dans n'importe quel langage"""
        self.logger.info(' Validation multi-langages du code corrige')
        
        corrected_code = state.get('corrected_code', '')
        original_code = state.get('code', '')
        detected_language = state.get('detected_language', 'unknown')
        corrected_language = state.get('corrected_language', detected_language)
        
        if not corrected_code:
            self.logger.warning(' Aucun code corrige à valider')
            state['validation'] = {'error': 'Pas de code corrige'}
            return state
        
        self.logger.info(f' Validation du code {corrected_language}')
        
        # 1. VALIDATION SYNTAXE via LLM (dynamique)
        syntax_check = validate_syntax_with_llm(corrected_code, corrected_language)
        
        validation = {
            'language': corrected_language,
            'syntax_validation': syntax_check,
            'approved': False
        }
        
        # 2. VALIDATION APPROFONDIE PAR LLM (100% dynamique)
        prompt = f"""Tu es un validateur expert pour {corrected_language}.

LANGAGE: {corrected_language}

CODE ORIGINAL:
```{detected_language}
{original_code}
```

CODE CORRIGe:
```{corrected_language}
{corrected_code}
```

🔍 VALIDATION COMPLÈTE:

1. **Syntaxe**: Le code corrige est-il syntaxiquement valide en {corrected_language}?
2. **Bugs**: Tous les bugs ont-ils ete corriges?
3. **Fonctionnalite**: La fonctionnalite est-elle preservee?
4. **Nouveaux bugs**: Y a-t-il de nouvelles erreurs introduites?
5. **Qualite**: Le code respecte-t-il les standards de {corrected_language}?
6. **Securite**: Pas de failles de securite introduites?

Reponds en JSON:
{{
    "is_syntactically_valid": true/false,
    "all_bugs_fixed": true/false,
    "functionality_preserved": true/false,
    "new_bugs_introduced": true/false,
    "code_quality": "excellent/good/average/poor",
    "security_check": "pass/fail",
    "final_verdict": "APPROVED/REJECTED",
    "explanation": "explication courte"
}}
"""
        
        try:
            llm_response = self.invoke_llm(prompt)
            validation['llm_validation'] = llm_response
            
            # Decision d'approbation (cherche "APPROVED" dans la reponse)
            if 'APPROVED' in llm_response.upper():
                validation['approved'] = True
                self.logger.info(f' Code {corrected_language} valide et APPROUVe')
            else:
                self.logger.warning(f' Code {corrected_language} REJETe')
                
        except Exception as e:
            self.logger.error(f' Erreur validation: {e}')
            validation['llm_validation'] = str(e)
        
        state['validation'] = validation
        state['current_step'] = 'validated'
        
        return state