from abc import ABC, abstractmethod
from typing import Dict, Any
from src.utils.llm_helper import get_llm
from src.utils.logger import setup_logger

class BaseAgent(ABC):
    '''Classe de base pour tous les agents du swarm'''
    
    def __init__(self, name: str, role: str, model: str = None, temperature: float = None):
        self.name = name
        self.role = role
        self.model = model
        self.temperature = temperature
        self.llm = get_llm(model, temperature)
        self.logger = setup_logger(f'Agent.{name}')
        
    @abstractmethod
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        '''
        Traite l'état et retourne un nouvel état modifié
        
        Args:
            state: État actuel du workflow
            
        Returns:
            État modifié
        '''
        pass
    
    def invoke_llm(self, prompt: str) -> str:
        '''Appelle le LLM avec un prompt'''
        self.logger.info(f'{self.name} invoque le LLM')
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            self.logger.error(f'Erreur LLM: {e}')
            raise
    
    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, role={self.role})'
