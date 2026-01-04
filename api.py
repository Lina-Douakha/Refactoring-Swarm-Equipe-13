import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from colorama import Fore, Style, init

# Initialiser colorama
init(autoreset=True)

# Charger les variables d'environnement
load_dotenv()

def test_google_api():
    """Teste la connexion à l'API Google Studio AI avec différents modèles"""
    
    print(f"{Fore.CYAN}{'='*50}")
    print(f"{Fore.CYAN}Test de l'API Google Studio AI")
    print(f"{Fore.CYAN}{'='*50}\n")
    
    # Récupérer la clé API
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print(f"{Fore.RED}  Erreur: La clé GOOGLE_API_KEY n'est pas trouvée dans le fichier .env")
        print(f"{Fore.YELLOW}  Assurez-vous d'avoir une ligne: GOOGLE_API_KEY=votre_cle")
        return False
    
    print(f"{Fore.GREEN}✓ Clé API trouvée dans .env")
    print(f"{Fore.BLUE}  Clé: {api_key[:10]}...{api_key[-5:]}\n")
    
    # Liste des modèles à tester (basés sur les modèles disponibles)
    models_to_test = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-pro-latest"
    ]
    
    for model_name in models_to_test:
        try:
            print(f"{Fore.CYAN}Test du modèle: {model_name}")
            
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=api_key,
                temperature=0.7
            )
            
            # Tester avec une requête simple
            response = llm.invoke("Dis bonjour en une phrase")
            
            print(f"{Fore.GREEN}✓ SUCCÈS avec le modèle: {model_name}\n")
            print(f"{Fore.YELLOW}{'='*50}")
            print(f"{Fore.WHITE}Réponse du modèle:")
            print(f"{Fore.WHITE}{response.content}")
            print(f"{Fore.YELLOW}{'='*50}\n")
            
            print(f"{Fore.GREEN}  TEST RÉUSSI!")
            print(f"{Fore.GREEN}➜ Utilisez ce nom de modèle dans votre projet: {model_name}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}✗ Échec avec {model_name}")
            print(f"{Fore.RED}  Erreur: {str(e)[:100]}...\n")
            continue
    
    # Si aucun modèle ne fonctionne
    print(f"{Fore.RED}{'='*50}")
    print(f"{Fore.RED}  Aucun modèle n'a fonctionné")
    print(f"{Fore.YELLOW}\n  Solutions possibles:")
    print(f"{Fore.YELLOW}   1. Vérifiez que votre clé API est activée sur:")
    print(f"{Fore.WHITE}      https://makersuite.google.com/app/apikey")
    print(f"{Fore.YELLOW}   2. La version langchain-google-genai==0.0.9 est ancienne")
    print(f"{Fore.YELLOW}      Demandez au prof si vous pouvez utiliser 0.0.11+")
    print(f"{Fore.YELLOW}   3. Activez l'API Gemini sur Google Cloud Console")
    return False

if __name__ == "__main__":
    test_google_api()