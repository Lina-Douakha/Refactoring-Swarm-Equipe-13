"""
Script pour lister tous les modèles Gemini disponibles
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configurer l'API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY non trouvée dans .env")
    exit(1)

genai.configure(api_key=api_key)

print("="*70)
print("📋 MODÈLES GEMINI DISPONIBLES")
print("="*70)

try:
    models = genai.list_models()
    
    generation_models = []
    
    for model in models:
        # Filtrer les modèles qui supportent generateContent
        if 'generateContent' in model.supported_generation_methods:
            generation_models.append(model.name)
            print(f"\n✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description[:100]}...")
    
    print("\n" + "="*70)
    print("🎯 MODÈLES RECOMMANDÉS POUR VOTRE PROJET :")
    print("="*70)
    
    # Extraire les noms courts
    for full_name in generation_models:
        short_name = full_name.replace('models/', '')
        if 'flash' in short_name.lower():
            print(f"⚡ {short_name}")
        elif 'pro' in short_name.lower():
            print(f"🚀 {short_name}")
    
except Exception as e:
    print(f"❌ Erreur : {str(e)}")