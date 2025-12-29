
from langgraph.graph import StateGraph, END
from src.core.state_manager import AgentState
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.bug_detector_agent import BugDetectorAgent
from src.agents.refactor_agent import RefactorAgent
from src.agents.validator_agent import ValidatorAgent
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def create_workflow():
    '''Crée le workflow LangGraph du système'''
    
    # Initialiser les agents
    analyzer = AnalyzerAgent()
    bug_detector = BugDetectorAgent()
    refactor = RefactorAgent()
    validator = ValidatorAgent()
    
    # Fonctions de nœuds
    def analyze_node(state: AgentState) -> AgentState:
        logger.info('📊 Nœud: Analyse')
        return analyzer.process(state)
    
    def detect_bugs_node(state: AgentState) -> AgentState:
        logger.info('🐛 Nœud: Détection de bugs')
        return bug_detector.process(state)
    
    def refactor_node(state: AgentState) -> AgentState:
        logger.info('🔧 Nœud: Refactoring')
        return refactor.process(state)
    
    def validate_node(state: AgentState) -> AgentState:
        logger.info('✅ Nœud: Validation')
        return validator.process(state)
    
    # Fonction de décision
    def should_retry(state: AgentState) -> str:
        '''Décide si on doit réessayer ou terminer'''
        validation = state.get('validation', {})
        iterations = state.get('iterations', 0)
        
        if validation.get('approved', False):
            logger.info('✅ Code approuvé - FIN')
            return 'end'
        elif iterations >= 3:
            logger.warning('⚠️  Max iterations atteintes - FIN')
            return 'end'
        else:
            logger.info('🔄 Nouvelle itération nécessaire')
            state['iterations'] = iterations + 1
            return 'retry'
    
    # Créer le graphe
    workflow = StateGraph(AgentState)
    
    # Ajouter les nœuds
    workflow.add_node('analyze', analyze_node)
    workflow.add_node('detect_bugs', detect_bugs_node)
    workflow.add_node('refactor', refactor_node)
    workflow.add_node('validate', validate_node)
    
    # Définir les transitions
    workflow.set_entry_point('analyze')
    workflow.add_edge('analyze', 'detect_bugs')
    workflow.add_edge('detect_bugs', 'refactor')
    workflow.add_edge('refactor', 'validate')
    
    # Ajouter la logique de décision
    workflow.add_conditional_edges(
        'validate',
        should_retry,
        {
            'retry': 'refactor',  # Réessayer le refactoring
            'end': END            # Terminer
        }
    )
    
    return workflow.compile()