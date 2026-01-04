import os
import requests
from dotenv import load_dotenv
from colorama import Fore, init

init(autoreset=True)
load_dotenv()

def test_direct_api():
    """Teste l'API Google directement sans LangChain"""
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}Test Direct de l'API Google Gemini")
    print(f"{Fore.CYAN}{'='*60}\n")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print(f"{Fore.RED}  Clé API non trouvée")
        return
    
    print(f"{Fore.GREEN}✓ Clé API: {api_key[:10]}...{api_key[-5:]}\n")
    
    # 1. Lister les modèles disponibles
    print(f"{Fore.CYAN}📋 Étape 1: Liste des modèles disponibles\n")
    
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(list_url)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            
            if not models:
                print(f"{Fore.RED}  Aucun modèle disponible")
                return
            
            print(f"{Fore.GREEN}✓ {len(models)} modèles trouvés:\n")
            
            generation_models = []
            for model in models:
                name = model.get('name', '')
                display_name = model.get('displayName', '')
                methods = model.get('supportedGenerationMethods', [])
                
                if 'generateContent' in methods:
                    generation_models.append(name)
                    print(f"{Fore.GREEN}✓ {name}")
                    print(f"{Fore.WHITE}  Nom: {display_name}")
                    print(f"{Fore.CYAN}  Méthodes: {', '.join(methods)}\n")
            
            if not generation_models:
                print(f"{Fore.RED}  Aucun modèle ne supporte 'generateContent'")
                print(f"{Fore.YELLOW}\n  Votre clé API n'a peut-être pas accès à Gemini")
                print(f"{Fore.YELLOW}   Allez sur https://aistudio.google.com/apikey")
                print(f"{Fore.YELLOW}   et assurez-vous que l'API Gemini est activée")
                return
            
            # 2. Tester le premier modèle disponible
            test_model = generation_models[0]
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}  Étape 2: Test du modèle {test_model}\n")
            
            # Extraire le nom court du modèle
            model_short_name = test_model.replace('models/', '')
            
            generate_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_short_name}:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": "Dis bonjour en une phrase courte"
                    }]
                }]
            }
            
            response = requests.post(generate_url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                
                print(f"{Fore.GREEN}  TEST RÉUSSI!\n")
                print(f"{Fore.YELLOW}{'='*60}")
                print(f"{Fore.WHITE}Réponse du modèle:")
                print(f"{Fore.WHITE}{text}")
                print(f"{Fore.YELLOW}{'='*60}\n")
                
                print(f"{Fore.GREEN}➜ Modèle à utiliser dans LangChain: {model_short_name}")
                
            else:
                print(f"{Fore.RED}  Erreur {response.status_code}")
                print(f"{Fore.RED}{response.text[:200]}")
                
        else:
            print(f"{Fore.RED}  Erreur {response.status_code}")
            print(f"{Fore.RED}{response.text[:200]}")
            
            if response.status_code == 403:
                print(f"\n{Fore.YELLOW}  Erreur 403: API non activée")
                print(f"{Fore.YELLOW}   1. Allez sur https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com")
                print(f"{Fore.YELLOW}   2. Activez l'API 'Generative Language API'")
                
    except Exception as e:
        print(f"{Fore.RED}  Erreur: {str(e)}")

if __name__ == "__main__":
    test_direct_api()