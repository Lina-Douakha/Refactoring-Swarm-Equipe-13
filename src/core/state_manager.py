
from typing import TypedDict, Annotated
from langgraph.graph import add_messages

class AgentState(TypedDict):
    '''État partagé entre tous les agents'''
    # Input
    code: str                           # Code original bugué
    task_description: str               # Description de la tâche
    
    # Processing
    current_step: str                   # Étape actuelle du workflow
    analysis: dict                      # Résultat de l'analyse
    bugs: dict                          # Bugs détectés
    corrected_code: str                 # Code corrigé
    validation: dict                    # Résultat de la validation
    
    # Metadata
    iterations: int                     # Nombre d'itérations
    errors: list                        # Erreurs rencontrées
    messages: Annotated[list, add_messages]  # Historique des messages
