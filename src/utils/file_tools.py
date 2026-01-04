import os

def read_file(path):
    """Lit un fichier et retourne son contenu."""
    if not os.path.exists(path):
        print(f"[ERROR] Fichier {path} introuvable.")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    """Écrit du contenu dans un fichier."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
