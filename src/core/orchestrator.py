
from typing import Dict, Any
from src.core.workflow import create_workflow
from src.core.state_manager import AgentState
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RefactoringOrchestrator:
    '''Orchestrateur principal du système de refactoring'''
    
    def __init__(self):
        self.workflow = create_workflow()
        logger.info('🚀 Orchestrateur initialisé')
    
    def process_code(self, code: str, description: str = '') -> Dict[str, Any]:
        '''
        Traite un code bugué et retourne le code corrigé
        
        Args:
            code: Code source bugué
            description: Description optionnelle de la tâche
            
        Returns:
            Dictionnaire avec le code corrigé et les métadonnées
        '''
        logger.info('=' * 60)
        logger.info('🎯 DÉBUT DU TRAITEMENT')
        logger.info('=' * 60)
        
        # État initial
        initial_state: AgentState = {
            'code': code,
            'task_description': description,
            'current_step': 'init',
            'analysis': {},
            'bugs': {},
            'corrected_code': '',
            'validation': {},
            'iterations': 0,
            'errors': [],
            'messages': []
        }
        
        try:
            # Exécuter le workflow
            final_state = self.workflow.invoke(initial_state)
            
            logger.info('=' * 60)
            logger.info('✅ TRAITEMENT TERMINÉ')
            logger.info('=' * 60)
            
            return {
                'success': True,
                'original_code': code,
                'corrected_code': final_state.get('corrected_code', code),
                'validation': final_state.get('validation', {}),
                'analysis': final_state.get('analysis', {}),
                'bugs': final_state.get('bugs', {}),
                'iterations': final_state.get('iterations', 0),
                'approved': final_state.get('validation', {}).get('approved', False)
            }
            
        except Exception as e:
            logger.error(f'❌ Erreur lors du traitement: {e}')
            return {
                'success': False,
                'error': str(e),
                'original_code': code,
                'corrected_code': code
            }