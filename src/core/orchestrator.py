from typing import Dict, Any
from src.core.workflow import create_workflow
from src.core.state_manager import AgentState
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RefactoringOrchestrator:
    """Orchestrateur principal du système de refactoring MULTI-LANGAGES"""
    
    def __init__(self):
        self.workflow = create_workflow()
        logger.info('🚀 Orchestrateur multi-langages initialisé')
    
    def process_code(self, code: str, description: str = '', filename: str = '') -> Dict[str, Any]:
        """
        Traite un code bugué et retourne le code corrigé - TOUS LANGAGES
        
        Args:
            code: Code source bugué
            description: Description optionnelle de la tâche
            filename: Nom du fichier (aide à la détection du langage)
            
        Returns:
            Dictionnaire avec le code corrigé et les métadonnées
        """
        logger.info('=' * 60)
        logger.info('🎯 DÉBUT DU TRAITEMENT MULTI-LANGAGES')
        if filename:
            logger.info(f'📄 Fichier: {filename}')
        logger.info('=' * 60)
        
        # État initial (ajout de filename et detected_language)
        initial_state: AgentState = {
            'code': code,
            'filename': filename,  # ✅ AJOUTÉ
            'task_description': description,
            'current_step': 'init',
            'detected_language': 'unknown',  # ✅ AJOUTÉ
            'analysis': {},
            'bugs': {},
            'corrected_code': '',
            'corrected_language': '',  # ✅ AJOUTÉ
            'validation': {},
            'iterations': 0,
            'errors': [],
            'messages': []
        }
        
        try:
            # Exécuter le workflow
            final_state = self.workflow.invoke(initial_state)
            
            detected_lang = final_state.get('detected_language', 'unknown')
            
            logger.info('=' * 60)
            logger.info(f'✅ TRAITEMENT TERMINÉ [{detected_lang}]')
            logger.info('=' * 60)
            
            return {
                'success': True,
                'original_code': code,
                'corrected_code': final_state.get('corrected_code', code),
                'detected_language': detected_lang,  # ✅ AJOUTÉ
                'corrected_language': final_state.get('corrected_language', detected_lang),  # ✅ AJOUTÉ
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
                'corrected_code': code,
                'detected_language': 'unknown'
            }