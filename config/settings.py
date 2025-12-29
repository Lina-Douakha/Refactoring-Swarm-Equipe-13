import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_BASE_URL = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    
    # Model Configuration
    PRIMARY_MODEL = os.getenv('PRIMARY_MODEL', 'openai/gpt-4-turbo-preview')
    FALLBACK_MODEL = os.getenv('FALLBACK_MODEL', 'anthropic/claude-3-sonnet')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.2'))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '2000'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Paths
    DATA_INPUT_PATH = 'data/input'
    DATA_OUTPUT_PATH = 'data/output'
    TEST_CASES_PATH = 'data/test_cases'
    
    @classmethod
    def validate(cls):
        if not cls.OPENROUTER_API_KEY:
            raise ValueError('OPENROUTER_API_KEY non configurée dans .env')
        return True

settings = Settings()