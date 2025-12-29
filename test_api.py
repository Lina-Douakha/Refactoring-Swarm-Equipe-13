
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()

print('🔍 Test de configuration OpenRouter...')

# Vérification des variables
api_key = os.getenv('OPENROUTER_API_KEY')
base_url = os.getenv('OPENROUTER_BASE_URL')
model = os.getenv('PRIMARY_MODEL')

print(f'✅ OPENROUTER_API_KEY: {"Configurée" if api_key else "❌ Manquante"}')
print(f'✅ Base URL: {base_url}')
print(f'✅ Modèle: {model}')

if api_key:
    try:
        print('\n🚀 Test d\'appel API...')
        llm = ChatOpenAI(
            model=model,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=0.2
        )
        
        response = llm.invoke('Réponds juste \"OK\" pour confirmer que tu fonctionnes')
        print(f'✅ API fonctionne!')
        print(f'Réponse: {response.content}')
        
    except Exception as e:
        print(f'❌ Erreur API: {e}')
        print('Vérifiez votre clé et votre crédit sur https://openrouter.ai')
else:
    print('\n⚠️  Clé API manquante - ajoutez-la dans .env')