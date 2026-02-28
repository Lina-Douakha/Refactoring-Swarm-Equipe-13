import pytest
from code2 import UTILISATEURS, authentifier, changer_mdp

@pytest.fixture(autouse=True)
def reset_users():
    """Fixture pour réinitialiser la base d'utilisateurs avant chaque test."""
    original_users = UTILISATEURS.copy()
    yield
    # Restaure l'état original après le test
    # Ceci est important si changer_mdp modifie UTILISATEURS directement
    # et que les tests suivants dépendent de l'état initial.
    # Dans ce cas précis, changer_mdp ne modifie pas UTILISATEURS en dehors
    # de son scope si on ne lui passe pas une référence mutable.
    # Cependant, une bonne pratique serait de le faire si nécessaire.
    # Pour cet exemple, nous allons réinitialiser la liste pour garantir
    # que chaque test démarre avec les mêmes données.
    UTILISATEURS.clear()
    UTILISATEURS.update(original_users)


def test_authentifier_success():
    """Teste l'authentification réussie d'un utilisateur valide."""
    assert authentifier("admin", "1234") is True
    assert authentifier("user", "abcd") is True

def test_authentifier_failure_wrong_password():
    """Teste l'échec d'authentification avec un mot de passe incorrect."""
    assert authentifier("admin", "wrongpassword") is False

def test_authentifier_failure_unknown_user():
    """Teste l'échec d'authentification avec un utilisateur inconnu."""
    assert authentifier("unknownuser", "password") is False

def test_authentifier_empty_credentials():
    """Teste l'authentification avec des identifiants vides."""
    assert authentifier("", "") is False
    assert authentifier("admin", "") is False
    assert authentifier("", "1234") is False

def test_changer_mdp_success():
    """Teste le changement de mot de passe réussi avec l'ancien mot de passe correct."""
    login = "user"
    ancien_mdp = "abcd"
    nouveau_mdp = "new_secure_password"
    assert authentifier(login, ancien_mdp) is True
    changer_mdp(login, ancien_mdp, nouveau_mdp)
    assert authentifier(login, nouveau_mdp) is True
    assert authentifier(login, ancien_mdp) is False # L'ancien mot de passe ne doit plus fonctionner

def test_changer_mdp_failure_wrong_old_password():
    """Teste le changement de mot de passe échoué avec un ancien mot de passe incorrect."""
    login = "user"
    ancien_mdp_incorrect = "wrongpassword"
    nouveau_mdp = "new_secure_password"
    mdp_original = UTILISATEURS[login]
    changer_mdp(login, ancien_mdp_incorrect, nouveau_mdp)
    assert authentifier(login, nouveau_mdp) is False # Le nouveau mot de passe ne doit pas être appliqué
    assert authentifier(login, mdp_original) is True # L'ancien mot de passe doit rester le même

def test_changer_mdp_for_non_existent_user():
    """Teste le changement de mot de passe pour un utilisateur qui n'existe pas."""
    login = "nonexistent"
    ancien_mdp = "anypassword"
    nouveau_mdp = "new_password"
    initial_users_count = len(UTILISATEURS)
    changer_mdp(login, ancien_mdp, nouveau_mdp)
    assert login not in UTILISATEURS # L'utilisateur ne devrait pas être ajouté
    assert len(UTILISATEURS) == initial_users_count