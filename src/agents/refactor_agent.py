from typing import Dict, Any
from src.agents.base_agent import BaseAgent
from src.utils.code_utils import extract_code_blocks

class RefactorAgent(BaseAgent):
    """Agent qui corrige et refactorise le code TOUS LANGAGES"""
    
    def __init__(self):
        super().__init__(
            name='Refactor',
            role='Multi-Language Code Refactoring',
            temperature=0.3
        )
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Corrige le code bugue dans n'importe quel langage"""
        self.logger.info('🔧 Refactoring multi-langages en cours')
        
        code = state.get('code', '')
        bugs = state.get('bugs', {})
        analysis = state.get('analysis', {})
        detected_language = state.get('detected_language', 'unknown')
        
        self.logger.info(f' Refactoring du code {detected_language}')
        
        # PROMPT 100% DYNAMIQUE (pas de specificite langage)
        prompt = f"""Tu es un expert en refactoring de code {detected_language}.

LANGAGE: {detected_language}

CODE ORIGINAL:
```{detected_language}
{code}
```

BUGS DeTECTeS:
{bugs.get('llm_detected', 'Aucun')}

ANALYSE:
{analysis.get('llm_analysis', 'Aucune')}

 MISSION:
1. Corrige TOUS les bugs identifies
2. Ameliore la qualite du code
3. Applique les meilleures pratiques de {detected_language}
4. Garde la même fonctionnalite

 IMPORTANT:
- Reponds UNIQUEMENT avec le code corrige
- Utilise la syntaxe ```{detected_language}
- PAS d'explications, JUSTE le code
"""
        
        try:
            llm_response = self.invoke_llm(prompt)
            
            # Extraire le code corrige (supporte tous langages)
            code_blocks = extract_code_blocks(llm_response)
            
            if code_blocks:
                # Prend le premier bloc (lang, code)
                lang, corrected_code = code_blocks[0]
                state['corrected_code'] = corrected_code
                state['corrected_language'] = lang
                self.logger.info(f' Code {detected_language} corrige avec succès')
            else:
                # Fallback: prend toute la reponse
                state['corrected_code'] = llm_response
                state['corrected_language'] = detected_language
                self.logger.warning(' Pas de bloc de code trouve, utilisation de la reponse brute')
                
        except Exception as e:
            self.logger.error(f' Erreur refactoring: {e}')
            state['corrected_code'] = code  # Garde le code original
            state['refactor_error'] = str(e)
        
        state['current_step'] = 'refactored'
        
        return state