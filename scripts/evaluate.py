
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.core.orchestrator import RefactoringOrchestrator
from pathlib import Path
import json

def evaluate_on_dataset(input_dir: str, output_dir: str):
    '''Évalue le système sur un dataset de code bugué'''
    
    orchestrator = RefactoringOrchestrator()
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = []
    
    # Traiter tous les fichiers Python dans input_dir
    for file in input_path.glob('*.py'):
        print(f'\n🔍 Traitement de: {file.name}')
        
        with open(file, 'r', encoding='utf-8') as f:
            buggy_code = f.read()
        
        result = orchestrator.process_code(buggy_code)
        
        # Sauvegarder le code corrigé
        output_file = output_path / file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['corrected_code'])
        
        results.append({
            'file': file.name,
            'success': result['success'],
            'approved': result.get('approved', False),
            'iterations': result.get('iterations', 0)
        })
        
        print(f'  ✅ Sauvegardé: {output_file}')
    
    # Sauvegarder le rapport
    report_file = output_path / 'evaluation_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f'\n📊 Rapport sauvegardé: {report_file}')
    
    # Statistiques
    total = len(results)
    success = sum(1 for r in results if r['approved'])
    print(f'\n✅ Résultats: {success}/{total} codes validés ({success/total*100:.1f}%)')

if __name__ == '__main__':
    evaluate_on_dataset('data/input', 'data/output')