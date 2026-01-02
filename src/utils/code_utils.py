import re
from typing import Dict, List, Optional, Tuple

def extract_code_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Extrait les blocs de code d'un texte markdown
    Retourne: Liste de tuples (langage_déclaré, code)
    """
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    return [(lang or 'unknown', code) for lang, code in matches]

def count_lines(code: str) -> int:
    """Compte les lignes de code (sans lignes vides)"""
    lines = code.split('\n')
    return len([l for l in lines if l.strip()])