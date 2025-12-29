import ast
import re
from typing import Dict, List, Optional

def extract_code_blocks(text: str) -> List[str]:
    '''Extrait les blocs de code d'un texte markdown'''
    pattern = r'```(?:python)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return matches

def is_valid_python(code: str) -> bool:
    '''Vérifie si le code Python est syntaxiquement valide'''
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def get_syntax_errors(code: str) -> Optional[str]:
    '''Retourne les erreurs de syntaxe s'il y en a'''
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return f'Ligne {e.lineno}: {e.msg}'

def count_lines(code: str) -> int:
    '''Compte le nombre de lignes de code (sans commentaires/lignes vides)'''
    lines = code.split('\n')
    return len([l for l in lines if l.strip() and not l.strip().startswith('#')])
