
from langchain_openai import ChatOpenAI
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

def get_llm(model: str = None, temperature: float = None):
    '''
    Crée une instance LLM configurée pour OpenRouter
    
    Args:
        model: Nom du modèle (par défaut PRIMARY_MODEL)
        temperature: Température (par défaut settings.TEMPERATURE)
    
    Returns:
        ChatOpenAI: Instance configurée
    '''
    model_name = model or settings.PRIMARY_MODEL
    temp = temperature if temperature is not None else settings.TEMPERATURE
    
    logger.info(f'Initialisation LLM: {model_name} (temp={temp})')
    
    return ChatOpenAI(
        model=model_name,
        temperature=temp,
        openai_api_key=settings.OPENROUTER_API_KEY,
        openai_api_base=settings.OPENROUTER_BASE_URL,
        max_tokens=settings.MAX_TOKENS
    )