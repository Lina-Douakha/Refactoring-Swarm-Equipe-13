# ============================================================================
# TEST DU SWARM CONTROLLER
# ============================================================================

import os
import sys

# Ajouter le répertoire racine au path si nécessaire
if os.path.dirname(__file__) not in sys.path:
    sys.path.insert(0, os.path.dirname(__file__))

from src.agents.auditor import AuditorAgent
from src.agents.fixer import FixerAgent
from src.agents.judge import JudgeAgent

def test_swarm():
    """Test simple du workflow complet"""
    
    print("="*70)
    print("🧪 TEST DU WORKFLOW COMPLET")
    print("="*70)
    
    target_dir = "sandbox"
    model_name = "gemini-2.5-flash-lite"
    
    try:
        # Initialisation des agents
        print("\n🔧 Initialisation des agents...")
        auditor = AuditorAgent(model_name=model_name)
        fixer = FixerAgent(model_name=model_name)
        judge = JudgeAgent(model_name=model_name)
        print("✅ Tous les agents sont prêts\n")
        
        # ÉTAPE 1 : AUDITOR
        print("="*70)
        print("📊 ÉTAPE 1/3 : AUDITOR - Analyse du code")
        print("="*70)
        
        audit_report = auditor.analyze(target_dir=target_dir)
        
        print(f"\n✅ Analyse terminée :")
        print(f"   - Fichiers analysés : {len(audit_report['files_analyzed'])}")
        print(f"   - Problèmes détectés : {audit_report['total_issues']}")
        
        # ÉTAPE 2 : FIXER
        print("\n" + "="*70)
        print("🔧 ÉTAPE 2/3 : FIXER - Correction du code")
        print("="*70)
        
        if audit_report['total_issues'] == 0:
            print("\n✅ Aucun problème à corriger")
            fix_result = {"files_fixed": [], "total_fixes": 0}
        else:
            fix_result = fixer.fix(
                audit_report=audit_report,
                target_dir=target_dir
            )
            print(f"\n✅ Corrections terminées :")
            print(f"   - Fichiers corrigés : {len(fix_result['files_fixed'])}")
            print(f"   - Corrections appliquées : {fix_result['total_fixes']}")
        
        # ÉTAPE 3 : JUDGE
        print("\n" + "="*70)
        print("⚖️  ÉTAPE 3/3 : JUDGE - Validation par tests")
        print("="*70)
        
        test_result = judge.test(target_dir=target_dir)
        
        print(f"\n📊 Résultats des tests :")
        print(f"   - Tests réussis : {test_result['passed']}")
        print(f"   - Tests échoués : {test_result['failed']}")
        
        # RÉSULTAT FINAL
        print("\n" + "="*70)
        if test_result["success"]:
            print("🎉 SUCCÈS ! Tous les tests passent !")
            print("✅ Le workflow complet fonctionne correctement")
        else:
            print("⚠️  ÉCHEC : Certains tests ont échoué")
            if test_result.get("recommendations"):
                print("\n💡 Recommandations :")
                for rec in test_result["recommendations"]:
                    print(f"   - {rec}")
        print("="*70)
        
        return test_result["success"]
        
    except Exception as e:
        print(f"\n❌ ERREUR : {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_swarm()
    exit(0 if success else 1)