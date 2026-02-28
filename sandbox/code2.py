"""Module d'authentification simple."""

UTILISATEURS = {
    "admin": "1234",
    "user": "abcd"
}


def authentifier(login, mot_de_passe):
    """Authentifie un utilisateur.

    Args:
        login (str): Le nom d'utilisateur.
        mot_de_passe (str): Le mot de passe de l'utilisateur.

    Returns:
        bool: True si l'utilisateur est authentifié, False sinon.
    """
    for u, mdp in UTILISATEURS.items():
        if u == login and mdp == mot_de_passe:
            return True
    return False


def changer_mdp(login, ancien, nouveau):
    """Change le mot de passe d'un utilisateur.

    Si l'ancien mot de passe est incorrect, le mot de passe
    de l'utilisateur n'est pas modifié.

    Args:
        login (str): Le nom d'utilisateur.
        ancien (str): L'ancien mot de passe.
        nouveau (str): Le nouveau mot de passe.
    """
    if authentifier(login, ancien):
        UTILISATEURS[login] = nouveau
    print("Mot de passe modifié")


if __name__ == "__main__":
    print(authentifier("user", "abcd"))
    changer_mdp("user", "faux", "123")
    print(UTILISATEURS)
    changer_mdp("user", "abcd", "123")
    print(UTILISATEURS)