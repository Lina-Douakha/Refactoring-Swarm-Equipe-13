
# ============================================================================
# TEST 2 : FIXER AGENT
# ============================================================================
# Fichier : test_fixer.py

from src.agents.fixer import FixerAgent
from src.agents.auditor import AuditorAgent
import json

def test_fixer():
    """Teste l'agent Fixer avec un rapport d'audit"""
    
    print("="*60)
    print("TEST DU FIXER AGENT")
    print("="*60)
    
    # Étape 1 : Générer un rapport avec l'Auditor
    print("\n📋 Étape 1 : Génération du rapport d'audit...")
    auditor = AuditorAgent(model_name="gemini-2.5-flash")
    audit_report = auditor.analyze(target_dir="sandbox")
    
    print(f"✅ Rapport généré : {audit_report['total_issues']} problème(s)")
    
    # Étape 2 : Corriger avec le Fixer
    print("\n🔧 Étape 2 : Correction des fichiers...")
    fixer = FixerAgent(model_name="gemini-2.5-flash")
    
    try:
        fix_result = fixer.fix(
            audit_report=audit_report,
            target_dir="sandbox"
        )
        
        # Afficher les résultats
        print("\n📊 RÉSULTAT DES CORRECTIONS :")
        print(json.dumps(fix_result, indent=2, ensure_ascii=False))
        
        # Vérifications
        assert "files_fixed" in fix_result, "Clé 'files_fixed' manquante"
        assert "total_fixes" in fix_result, "Clé 'total_fixes' manquante"
        assert "status" in fix_result, "Clé 'status' manquante"
        
        print("\n✅ TEST FIXER RÉUSSI !")
        print(f"   - {len(fix_result['files_fixed'])} fichier(s) corrigé(s)")
        print(f"   - {fix_result['total_fixes']} correction(s) appliquée(s)")
        
        return fix_result
        
    except Exception as e:
        print(f"\n❌ TEST FIXER ÉCHOUÉ : {str(e)}")
        raise

if __name__ == "__main__":
    test_fixer()
