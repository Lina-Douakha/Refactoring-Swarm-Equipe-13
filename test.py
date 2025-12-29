from dotenv import load_dotenv
import os

load_dotenv()

print('🔍 Test de configuration OpenRouter...')
print(f'✅ OPENROUTER_API_KEY configurée: {bool(os.getenv("OPENROUTER_API_KEY"))}')
print(f'✅ Base URL: {os.getenv("OPENROUTER_BASE_URL")}')
print(f'✅ Modèle primaire: {os.getenv("PRIMARY_MODEL")}')
print(f'✅ Temperature: {os.getenv("TEMPERATURE")}')
print('\n✅ Configuration OK!')