import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.core.orchestrator import RefactoringOrchestrator
from src.utils.language_detector import detect_language_with_llm
from pathlib import Path
import json

def is_likely_code_file(file_path: Path) -> bool:
    """
    Determine si un fichier est probablement du code (pas binaire)
    """
    # Ignorer les fichiers binaires et système courants
    ignore_extensions = {'.exe', '.dll', '.so', '.bin', '.jpg', '.png', 
                        '.gif', '.pdf', '.zip', '.tar', '.gz', '.mp4', 
                        '.mp3', '.doc', '.docx', '.xls', '.xlsx'}
    
    if file_path.suffix.lower() in ignore_extensions:
        return False
    
    # Verifier si le fichier est lisible comme texte
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(100)  # Lire les 100 premiers caractères
        return True
    except (UnicodeDecodeError, PermissionError):
        return False

def evaluate_on_dataset(input_dir: str, output_dir: str):
    """evalue le système sur un dataset de code bugue - DeTECTION AUTOMATIQUE ILLIMITeE"""
    
    orchestrator = RefactoringOrchestrator()
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = []
    
    #  ReCUPeRER TOUS LES FICHIERS (pas de limite d'extension)
    all_files = [f for f in input_path.rglob('*') 
                 if f.is_file() and is_likely_code_file(f)]
    
    if not all_files:
        print('  Aucun fichier de code trouve dans:', input_dir)
        return
    
    print(f'\n {len(all_files)} fichiers potentiels trouves')
    print(' Detection automatique du langage via LLM...\n')
    
    for file in all_files:
        print(f' Traitement de: {file.name}')
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                code_content = f.read()
        except Exception as e:
            print(f'    Erreur de lecture: {e}')
            continue
        
        #  DeTECTER LE LANGAGE DYNAMIQUEMENT
        print(f'   Detection du langage...')
        lang_info = detect_language_with_llm(code_content, file.name)
        detected_lang = lang_info.get('language', 'unknown')
        
        # Si c'est pas du code, ignorer
        if 'unknown' in detected_lang.lower() or 'text' in detected_lang.lower():
            print(f'    Ignore (pas du code)')
            continue
        
        print(f'   Langage: {detected_lang}')
        
        # Traiter le code
        result = orchestrator.process_code(
            code=code_content,
            filename=file.name
        )
        
        # Sauvegarder le code corrige
        output_file = output_path / file.name
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result.get('corrected_code', code_content))
        
        results.append({
            'file': file.name,
            'language': result.get('detected_language', detected_lang),
            'success': result.get('success', False),
            'approved': result.get('approved', False),
            'iterations': result.get('iterations', 0)
        })
        
        status = '' if result.get('approved') else '⚠️'
        print(f'  {status} Sauvegarde: {output_file}\n')
    
    # Sauvegarder le rapport
    report_file = output_path / 'evaluation_report.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f'\n Rapport sauvegarde: {report_file}')
    
    # Statistiques
    if not results:
        print('\n  Aucun fichier de code traite')
        return
    
    total = len(results)
    success = sum(1 for r in results if r['approved'])
    
    print(f'\n{"="*60}')
    print(f' ReSULTATS GLOBAUX: {success}/{total} codes valides ({success/total*100:.1f}%)')
    print(f'{"="*60}')
    
    # Statistiques detaillees par langage
    languages = {}
    for r in results:
        lang = r['language']
        if lang not in languages:
            languages[lang] = {'total': 0, 'approved': 0}
        languages[lang]['total'] += 1
        if r['approved']:
            languages[lang]['approved'] += 1
    
    print('\n Details par langage:')
    for lang, stats in sorted(languages.items()):
        rate = stats['approved'] / stats['total'] * 100
        print(f'  • {lang:15s}: {stats["approved"]}/{stats["total"]} ({rate:.1f}%)')

if __name__ == '__main__':
    evaluate_on_dataset('data/input', 'data/output')