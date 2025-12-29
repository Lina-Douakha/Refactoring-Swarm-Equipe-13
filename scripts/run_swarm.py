
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.core.orchestrator import RefactoringOrchestrator
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    '''Point d'entrée principal du système'''
    
    # Code bugué en exemple
    buggy_code = '''
def calculate_average(numbers):
    total = 0
    for num in numbers
        total += num
    return total / len(numbers)

result = calculate_average([1, 2, 3, 4, 5])
print(f'La moyenne est: {result}')
'''
    
    print('🐝 THE REFACTORING SWARM 🐝')
    print('=' * 60)
    print('\n📝 Code bugué à corriger:')
    print(buggy_code)
    print('=' * 60)
    
    # Créer l'orchestrateur
    orchestrator = RefactoringOrchestrator()
    
    # Traiter le code
    result = orchestrator.process_code(
        code=buggy_code,
        description='Corriger les erreurs de syntaxe et améliorer le code'
    )
    
    # Afficher les résultats
    print('\n' + '=' * 60)
    print('📊 RÉSULTATS')
    print('=' * 60)
    
    if result['success']:
        print(f'\n✅ Traitement réussi!')
        print(f'🔄 Itérations: {result["iterations"]}')
        print(f'✓ Approuvé: {result["approved"]}')
        
        print('\n🔧 CODE CORRIGÉ:')
        print('-' * 60)
        print(result['corrected_code'])
        print('-' * 60)
        
        if result['approved']:
            print('\n✅ Code validé et prêt à l\'utilisation!')
        else:
            print('\n⚠️  Code corrigé mais non validé - vérification manuelle recommandée')
    else:
        print(f'\n❌ Erreur: {result["error"]}')
    
    print('\n' + '=' * 60)

if __name__ == '__main__':
    main()