"""
Point d'entrée principal du Refactoring Swarm
Lancé par le Bot de Correction avec : python main.py --target_dir "./sandbox/dataset"
"""

import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment, ActionType


load_dotenv()


def main():
    """
    Point d'entrée principal du système.
    Lit les arguments, lance le Swarm, et retourne le statut final.
    """
    
    parser = argparse.ArgumentParser(
        description="The Refactoring Swarm - Système multi-agents de refactoring automatique"
    )
    parser.add_argument(
        "--target_dir", 
        type=str, 
        required=True,
        help="Dossier contenant le code Python à refactoriser"
    )
    parser.add_argument(
        "--max_iterations",
        type=int,
        default=50,
        help="Nombre maximum d'itérations (défaut: 50)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gemini-2.5-flash-lite",
        help="Modèle LLM à utiliser (défaut: gemini-2.5-flash-lite)"
    )
    parser.add_argument(
        "--generate_tests",
        action="store_true",
        help="Génère automatiquement des tests unitaires"
    )
    parser.add_argument(
        "--generate_docs",
        action="store_true",
        help="Génère automatiquement la documentation"
    )
    
    args = parser.parse_args()
    
    # Validation du dossier cible
    if not os.path.exists(args.target_dir):
        print(f"❌ ERREUR : Le dossier {args.target_dir} n'existe pas.")
        sys.exit(1)
    
    # Validation de la clé API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERREUR : La clé API GOOGLE_API_KEY n'est pas configurée dans le fichier .env")
        sys.exit(1)
    
    # Affichage de la configuration
    print("=" * 80)
    print("🔥 THE REFACTORING SWARM - DÉMARRAGE")
    print("=" * 80)
    print(f"📁 Dossier cible    : {args.target_dir}")
    print(f"🔄 Itérations max   : {args.max_iterations}")
    print(f"🤖 Modèle LLM       : {args.model}")
    print(f"🧪 Tests            : {'Activé' if args.generate_tests else 'Désactivé'}")
    print(f"📚 Documentation    : {'Activé' if args.generate_docs else 'Désactivé'}")
    print("=" * 80)
    
    log_experiment(
        agent_name="System",
        model_used="N/A",
        action=ActionType.ANALYSIS,
        details={
            "input_prompt": f"Initialisation du système sur {args.target_dir}",
            "output_response": f"Démarrage avec model={args.model}, max_iterations={args.max_iterations}",
            "target_directory": args.target_dir,
            "max_iterations": args.max_iterations,
            "model_used": args.model,
            "generate_tests": args.generate_tests,
            "generate_docs": args.generate_docs
        },
        status="SUCCESS"
    )
    
    try:
        from src.orchestrator.swarm_controller import run_refactoring_swarm
        
        print("\n🚀 Lancement du Swarm...\n")
        
        # Exécution du système
        result = run_refactoring_swarm(
            target_dir=args.target_dir,
            model_name=args.model,
            max_iterations=args.max_iterations,
            generate_tests=args.generate_tests,
            generate_docs=args.generate_docs
        )
        
        # Affichage du résultat
        print("\n" + "=" * 80)
        print("📊 RÉSULTAT FINAL")
        print("=" * 80)
        
        if result["success"]:
            print("✅ MISSION ACCOMPLIE !")
            print(f"   Le code a été refactorisé avec succès en {result['total_iterations']} itération(s).")
            
            log_experiment(
                agent_name="System",
                model_used=args.model,
                action=ActionType.ANALYSIS,
                details={
                    "input_prompt": "Finalisation du système",
                    "output_response": f"Succès en {result['total_iterations']} itérations",
                    "success": True,
                    "total_iterations": result['total_iterations'],
                    "history": result.get('history', [])
                },
                status="SUCCESS"
            )
            
            print("\n📝 Logs disponibles dans : logs/experiment_data.json")
            print("=" * 80)
            sys.exit(0)
            
        else:
            print("⚠️  MISSION INCOMPLÈTE")
            print(f"   Le système a effectué {result['total_iterations']} itération(s)")
            
            if result.get("max_iterations_reached"):
                print(f"   Raison : Nombre maximum d'itérations atteint ({args.max_iterations})")
            else:
                print("   Raison : Erreur durant l'exécution")
            
            log_experiment(
                agent_name="System",
                model_used=args.model,
                action=ActionType.DEBUG,
                details={
                    "input_prompt": "Finalisation du système",
                    "output_response": f"Échec après {result['total_iterations']} itérations",
                    "success": False,
                    "total_iterations": result['total_iterations'],
                    "max_iterations_reached": result.get("max_iterations_reached", False),
                    "history": result.get('history', [])
                },
                status="FAILURE"
            )
            
            print("\n📝 Consultez les logs pour plus de détails : logs/experiment_data.json")
            print("=" * 80)
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  INTERRUPTION UTILISATEUR (Ctrl+C)")
        print("   Le système a été arrêté manuellement.")
        
        log_experiment(
            agent_name="System",
            model_used=args.model,
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Exécution du système sur {args.target_dir}",
                "output_response": "Interruption manuelle par l'utilisateur",
                "interruption": "KeyboardInterrupt",
                "target_dir": args.target_dir
            },
            status="FAILURE"
        )
        
        print("\n📝 Consultez les logs pour plus de détails : logs/experiment_data.json")
        print("=" * 80)
        sys.exit(130)  # Code de sortie standard pour Ctrl+C
    
    except ImportError as e:
        print(f"\n❌ ERREUR D'IMPORT : {str(e)}")
        print("   Vérifiez que tous les modules sont correctement installés.")
        print("   Commande : pip install -r requirements.txt")
        
        log_experiment(
            agent_name="System",
            model_used="N/A",
            action=ActionType.DEBUG,
            details={
                "input_prompt": "Import des modules",
                "output_response": f"Erreur d'import : {str(e)}",
                "error_type": "ImportError"
            },
            status="FAILURE"
        )
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE : {str(e)}")
        print(f"   Type d'erreur : {type(e).__name__}")
        
        log_experiment(
            agent_name="System",
            model_used=args.model,
            action=ActionType.DEBUG,
            details={
                "input_prompt": f"Exécution du système sur {args.target_dir}",
                "output_response": f"Erreur critique : {str(e)}",
                "error_type": type(e).__name__,
                "target_dir": args.target_dir
            },
            status="FAILURE"
        )
        
        print("\n📝 Consultez les logs pour plus de détails : logs/experiment_data.json")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    main()