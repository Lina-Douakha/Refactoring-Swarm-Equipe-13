"""
Scripts de test pour valider chaque agent individuellement
"""

# ============================================================================
# TEST 1 : AUDITOR AGENT
# ============================================================================
# Fichier : test_auditor.py

from src.agents.auditor import AuditorAgent
import json

def test_auditor():
    """Teste l'agent Auditor sur le dossier sandbox"""
    
    print("="*60)
    print("TEST DE L'AUDITOR AGENT")
    print("="*60)
    
    # Initialiser l'agent
    auditor = AuditorAgent(model_name="gemini-2.5-flash")
    
    # Analyser le dossier sandbox
    sandbox_dir = "sandbox"
    
    try:
        report = auditor.analyze(target_dir=sandbox_dir)
        
        # Afficher le rapport
        print("\n📊 RAPPORT D'AUDIT :")
        print(json.dumps(report, indent=2, ensure_ascii=False))
        
        # Vérifications
        assert "files_analyzed" in report, "Clé 'files_analyzed' manquante"
        assert "total_issues" in report, "Clé 'total_issues' manquante"
        assert "issues" in report, "Clé 'issues' manquante"
        assert "recommendations" in report, "Clé 'recommendations' manquante"
        
        print("\n✅ TEST AUDITOR RÉUSSI !")
        print(f"   - {len(report['files_analyzed'])} fichier(s) analysé(s)")
        print(f"   - {report['total_issues']} problème(s) détecté(s)")
        
        return report
        
    except Exception as e:
        print(f"\n❌ TEST AUDITOR ÉCHOUÉ : {str(e)}")
        raise

if __name__ == "__main__":
    test_auditor()

