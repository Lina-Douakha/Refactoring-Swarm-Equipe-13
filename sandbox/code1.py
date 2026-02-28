"""Module de gestion des commandes clients."""

class Commande:
    """Classe représentant une commande client."""

    def __init__(self, client, produits):
        """Initialise une nouvelle commande.

        Args:
            client (str): Le nom du client.
            produits (list): Une liste de produits, où chaque produit est un tuple
                             (nom, prix, quantite).
        """
        self.client = client
        self.produits = produits

    def total(self):
        """Calcule le prix total de la commande.

        Returns:
            int: Le prix total de la commande.
        """
        total_prix = 0
        for _, prix, quantite in self.produits:
            total_prix += prix * quantite
        return total_prix

    def ajouter_produit(self, nom, prix, quantite):
        """Ajoute un produit à la commande.

        Args:
            nom (str): Le nom du produit.
            prix (int): Le prix du produit.
            quantite (int): La quantite du produit.

        Raises:
            ValueError: Si la quantite est negative.
        """
        if quantite < 0:
            raise ValueError("La quantite ne peut pas etre negative.")
        self.produits.append((nom, prix, quantite))


def total_commandes(commandes):
    """Calcule le total de toutes les commandes d'une liste.

    Args:
        commandes (list): Une liste d'objets Commande.

    Returns:
        int: Le total de toutes les commandes.
    """
    total_global = 0
    for commande in commandes:
        total_global += commande.total()
    return total_global


def ajouter_produit_globale(commande, nom, prix, quantite):
    """Ajoute un produit à une commande existante (fonction globale).

    Args:
        commande (Commande): L'objet Commande auquel ajouter le produit.
        nom (str): Le nom du produit.
        prix (int): Le prix du produit.
        quantite (int): La quantite du produit.

    Raises:
        ValueError: Si la quantite est negative.
    """
    if quantite < 0:
        raise ValueError("La quantite ne peut pas etre negative.")
    commande.produits.append((nom, prix, quantite))


if __name__ == "__main__":
    c1 = Commande("Ali", [("PC", 120000, 1)])
    c2 = Commande("Sara", [("Clavier", 3000, 2)])

    try:
        ajouter_produit_globale(c2, "Souris", 1500, -1)
    except ValueError as e:
        print(f"Erreur lors de l'ajout du produit : {e}")

    print("Total commandes :", total_commandes([c1, c2]))