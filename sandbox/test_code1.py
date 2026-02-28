"""Module de test pour le code de gestion des commandes."""

import pytest
from code1 import Commande, total_commandes, ajouter_produit_globale


@pytest.fixture
def commande_vide():
    """Fixture pour une commande vide.

    Returns:
        Commande: Une instance de Commande vide.
    """
    return Commande("Test Client", [])


@pytest.fixture
def commande_avec_produits():
    """Fixture pour une commande avec des produits.

    Returns:
        Commande: Une instance de Commande avec des produits.
    """
    return Commande("Test Client", [("Produit A", 100, 2), ("Produit B", 50, 1)])


@pytest.fixture
def liste_commandes():
    """Fixture pour une liste de commandes.

    Returns:
        list: Une liste d'instances de Commande.
    """
    cmd1 = Commande("Client 1", [("Item 1", 10, 2)])
    cmd2 = Commande("Client 2", [("Item 2", 20, 1), ("Item 3", 5, 3)])
    return [cmd1, cmd2]


def test_commande_total_vide(commande_vide):
    """Teste le total d'une commande vide."""
    assert commande_vide.total() == 0


def test_commande_total_avec_produits(commande_avec_produits):
    """Teste le total d'une commande avec des produits."""
    assert commande_avec_produits.total() == 250  # (100*2) + (50*1)


def test_commande_ajouter_produit_valide(commande_vide):
    """Teste l'ajout d'un produit valide à une commande."""
    commande_vide.ajouter_produit("Nouveau Produit", 25, 3)
    assert len(commande_vide.produits) == 1
    assert commande_vide.produits[0] == ("Nouveau Produit", 25, 3)
    assert commande_vide.total() == 75


def test_commande_ajouter_produit_quantite_negative(commande_vide):
    """Teste l'ajout d'un produit avec une quantité négative."""
    with pytest.raises(ValueError, match="La quantité ne peut pas être négative."):
        commande_vide.ajouter_produit("Produit Erreur", 10, -5)
    assert len(commande_vide.produits) == 0


def test_total_commandes_liste_vide():
    """Teste le total de commandes pour une liste vide."""
    assert total_commandes([]) == 0


def test_total_commandes_liste_non_vide(liste_commandes):
    """Teste le total de commandes pour une liste non vide."""
    # commande 1: 10 * 2 = 20
    # commande 2: (20 * 1) + (5 * 3) = 20 + 15 = 35
    # total: 20 + 35 = 55
    assert total_commandes(liste_commandes) == 55


def test_ajouter_produit_globale_valide(commande_avec_produits):
    """Teste l'ajout d'un produit via la fonction globale."""
    ajouter_produit_globale(commande_avec_produits, "Produit C", 75, 1)
    assert len(commande_avec_produits.produits) == 3
    assert commande_avec_produits.produits[2] == ("Produit C", 75, 1)
    assert commande_avec_produits.total() == 325  # 250 + 75


def test_ajouter_produit_globale_quantite_negative(commande_avec_produits):
    """Teste l'ajout d'un produit via la fonction globale avec quantité négative."""
    initial_len = len(commande_avec_produits.produits)
    initial_total = commande_avec_produits.total()
    with pytest.raises(ValueError, match="La quantité ne peut pas être négative."):
        ajouter_produit_globale(commande_avec_produits, "Produit Erreur Globale", 50, -2)
    assert len(commande_avec_produits.produits) == initial_len
    assert commande_avec_produits.total() == initial_total