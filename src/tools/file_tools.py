import os
import sys


try:
    from ..utils.sandbox_guard import is_path_safe
except (ImportError, ValueError):
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    from utils.sandbox_guard import is_path_safe

def read_file_safe(filepath: str, sandbox_dir: str = None) -> str:
    """
    Lit un fichier de manière sécurisée.
    
    Args:
        filepath: Chemin du fichier (peut être relatif ou absolu)
        sandbox_dir: Dossier sandbox (optionnel, par défaut "sandbox")
    
    Returns:
        str: Contenu du fichier
    """
    
    if sandbox_dir is None:
        sandbox_dir = os.path.abspath("sandbox")
    else:
        sandbox_dir = os.path.abspath(sandbox_dir)
    
    
    abs_path = os.path.abspath(filepath)
    
    
    if not abs_path.startswith(sandbox_dir):
        raise PermissionError(f" Accès refusé : {filepath} est hors du sandbox {sandbox_dir}")
    
    
    with open(abs_path, "r", encoding="utf-8") as f:
        return f.read()

def write_file_safe(filepath: str, content: str, sandbox_dir: str = None):
    """
    Écrit un fichier de manière sécurisée.
    
    Args:
        filepath: Chemin du fichier
        content: Contenu à écrire
        sandbox_dir: Dossier sandbox (optionnel)
    """
    if sandbox_dir is None:
        sandbox_dir = os.path.abspath("sandbox")
    else:
        sandbox_dir = os.path.abspath(sandbox_dir)
    
    
    abs_path = os.path.abspath(filepath)
    
    
    if not abs_path.startswith(sandbox_dir):
        raise PermissionError(f" Accès refusé : {filepath} est hors du sandbox")
    
    
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)

def list_python_files(directory: str) -> list:
    """
    Liste tous les fichiers .py dans un dossier.
    
    Args:
        directory: Chemin du dossier
        
    Returns:
        list: Liste des noms de fichiers .py
    """
    abs_dir = os.path.abspath(directory)
    
    if not os.path.exists(abs_dir):
        raise FileNotFoundError(f" Dossier introuvable : {abs_dir}")
    
    return [f for f in os.listdir(abs_dir) if f.endswith(".py")]

def get_file_content(filepath: str, sandbox_dir: str = None) -> str:
    """Alias de read_file_safe pour compatibilité."""
    return read_file_safe(filepath, sandbox_dir)