"""Module de tests pour le système de gestion bancaire."""
import pytest
from code4 import Utilisateur, Compte, ajouter_utilisateur, trouver_utilisateur, total_soldes, transfert, afficher_utilisateurs, UTILISATEURS

@pytest.fixture
def initial_data():
    """Fournit des données initiales pour les tests."""
    UTILISATEURS.clear()
    user1 = Utilisateur("Ali", "ali@mail.com", 20)
    user1.creer_compte(1000)
    user2 = Utilisateur("Sara", "sara@mail.com", 17)
    user2.creer_compte(500)
    return user1, user2

@pytest.fixture
def empty_users():
    """Assure que la liste UTILISATEURS est vide avant chaque test."""
    UTILISATEURS.clear()
    yield
    UTILISATEURS.clear()

def test_ajouter_utilisateur(empty_users):
    """Teste l'ajout d'un utilisateur."""
    user = ajouter_utilisateur("Bob", "bob@mail.com", 30)
    assert isinstance(user, Utilisateur)
    assert user.nom == "Bob"
    assert user.email == "bob@mail.com"
    assert user.age == 30
    assert len(UTILISATEURS) == 1

def test_trouver_utilisateur_present(initial_data):
    """Teste la recherche d'un utilisateur existant."""
    user1, _ = initial_data
    found_user = trouver_utilisateur(user1.email)
    assert found_user is not None
    assert found_user.nom == "Ali"

def test_trouver_utilisateur_absent(initial_data):
    """Teste la recherche d'un utilisateur inexistant."""
    found_user = trouver_utilisateur("unknown@mail.com")
    assert found_user is None

def test_utilisateur_est_majeur(initial_data):
    """Teste la méthode est_majeur pour un utilisateur majeur."""
    user1, _ = initial_data
    assert user1.est_majeur() is True

def test_utilisateur_est_mineur(initial_data):
    """Teste la méthode est_majeur pour un utilisateur mineur."""
    _, user2 = initial_data
    assert user2.est_majeur() is False

def test_compte_deposer_montant_positif(initial_data):
    """Teste le dépôt d'un montant positif sur un compte."""
    user1, _ = initial_data
    initial_solde = user1.compte.solde
    user1.compte.deposer(200)
    assert user1.compte.solde == initial_solde + 200
    assert ("DEPOT", 200) in user1.compte.historique

def test_compte_deposer_montant_negatif(initial_data):
    """Teste le dépôt d'un montant négatif sur un compte."""
    user1, _ = initial_data
    initial_solde = user1.compte.solde
    user1.compte.deposer(-100)
    assert user1.compte.solde == initial_solde
    assert ("DEPOT", -100) not in user1.compte.historique

def test_compte_retirer_montant_positif_solde_suffisant(initial_data):
    """Teste le retrait d'un montant positif avec un solde suffisant."""
    user1, _ = initial_data
    initial_solde = user1.compte.solde
    user1.compte.retirer(100)
    assert user1.compte.solde == initial_solde - 100
    assert ("RETRAIT", 100) in user1.compte.historique

def test_compte_retirer_montant_positif_solde_insuffisant(initial_data):
    """Teste le retrait d'un montant positif avec un solde insuffisant."""
    user1, _ = initial_data
    initial_solde = user1.compte.solde
    user1.compte.retirer(1500)
    assert user1.compte.solde == initial_solde
    assert ("RETRAIT", 1500) not in user1.compte.historique

def test_compte_retirer_montant_negatif(initial_data):
    """Teste le retrait d'un montant négatif sur un compte."""
    user1, _ = initial_data
    initial_solde = user1.compte.solde
    user1.compte.retirer(-100)
    assert user1.compte.solde == initial_solde
    assert ("RETRAIT", -100) not in user1.compte.historique

def test_total_soldes_vide(empty_users):
    """Teste le calcul du total des soldes lorsque la liste d'utilisateurs est vide."""
    assert total_soldes() == 0

def test_total_soldes_avec_utilisateurs(initial_data):
    """Teste le calcul du total des soldes avec des utilisateurs existants."""
    user1, user2 = initial_data
    expected_total = user1.compte.solde + user2.compte.solde
    assert total_soldes() == expected_total

def test_transfert_montant_positif_solde_suffisant(initial_data):
    """Teste un transfert de montant positif avec solde suffisant."""
    user1, user2 = initial_data
    initial_solde_source = user1.compte.solde
    initial_solde_dest = user2.compte.solde
    montant = 200
    transfert(user1, user2, montant)
    assert user1.compte.solde == initial_solde_source - montant
    assert user2.compte.solde == initial_solde_dest + montant
    assert ("RETRAIT", montant) in user1.compte.historique
    assert ("DEPOT", montant) in user2.compte.historique

def test_transfert_montant_negatif(initial_data):
    """Teste un transfert avec un montant négatif."""
    user1, user2 = initial_data
    initial_solde_source = user1.compte.solde
    initial_solde_dest = user2.compte.solde
    transfert(user1, user2, -100)
    assert user1.compte.solde == initial_solde_source
    assert user2.compte.solde == initial_solde_dest
    assert ("RETRAIT", -100) not in user1.compte.historique
    assert ("DEPOT", -100) not in user2.compte.historique

def test_transfert_solde_insuffisant(initial_data):
    """Teste un transfert avec un solde insuffisant sur le compte source."""
    user1, user2 = initial_data
    initial_solde_source = user1.compte.solde
    initial_solde_dest = user2.compte.solde
    transfert(user1, user2, 1500)
    assert user1.compte.solde == initial_solde_source
    assert user2.compte.solde == initial_solde_dest
    assert ("RETRAIT", 1500) not in user1.compte.historique
    assert ("DEPOT", 1500) not in user2.compte.historique

def test_transfert_compte_source_inexistant(empty_users):
    """Teste un transfert lorsque le compte source n'existe pas."""
    user_dest = Utilisateur("Dest", "dest@mail.com", 25)
    user_dest.creer_compte(1000)
    UTILISATEURS.append(user_dest)
    user_source_no_account = Utilisateur("SourceNo", "sourcenos@mail.com", 30)
    UTILISATEURS.append(user_source_no_account)

    initial_solde_dest = user_dest.compte.solde
    transfert(user_source_no_account, user_dest, 100)
    assert user_dest.compte.solde == initial_solde_dest

def test_transfert_compte_destination_inexistant(empty_users):
    """Teste un transfert lorsque le compte de destination n'existe pas."""
    user_source = Utilisateur("Source", "source@mail.com", 25)
    user_source.creer_compte(1000)
    UTILISATEURS.append(user_source)
    user_dest_no_account = Utilisateur("DestNo", "destnos@mail.com", 30)
    UTILISATEURS.append(user_dest_no_account)

    initial_solde_source = user_source.compte.solde
    transfert(user_source, user_dest_no_account, 100)
    assert user_source.compte.solde == initial_solde_source

def test_afficher_utilisateurs_output(initial_data, capsys):
    """Teste que afficher_utilisateurs() imprime les informations correctes."""
    afficher_utilisateurs()
    captured = capsys.readouterr()
    assert "Ali - ali@mail.com" in captured.out
    assert "Sara - sara@mail.com" in captured.out