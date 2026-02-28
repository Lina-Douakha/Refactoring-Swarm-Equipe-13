```markdown
# Module de gestion des commandes clients

## Description
Ce module Python fournit des classes et fonctions pour gérer les commandes clients, calculer les totaux et ajouter des produits aux commandes.

## Fonctions principales

### Classe `Commande`

**`__init__(self, client, produits)`**
Initialise une nouvelle commande.

*   **Args:**
    *   `client` (str): Le nom du client.
    *   `produits` (list): Une liste de produits, où chaque produit est un tuple (nom, prix, quantité).

**`total(self)`**
Calcule le prix total de la commande.

*   **Returns:**
    *   int: Le prix total de la commande.

**`ajouter_produit(self, nom, prix, quantite)`**
Ajoute un produit à la commande.

*   **Args:**
    *   `nom` (str): Le nom du produit.
    *   `prix` (int): Le prix du produit.
    *   `quantite` (int): La quantité du produit.
*   **Raises:**
    *   `ValueError`: Si la quantité est négative.

### Fonction `total_commandes(commandes)`

Calcule le total de toutes les commandes d'une liste.

*   **Args:**
    *   `commandes` (list): Une liste d'objets `Commande`.
*   **Returns:**
    *   int: Le total de toutes les commandes.

### Fonction `ajouter_produit_globale(commande, nom, prix, quantite)`

Ajoute un produit à une commande existante (fonction globale).

*   **Args:**
    *   `commande` (Commande): L'objet `Commande` auquel ajouter le produit.
    *   `nom` (str): Le nom du produit.
    *   `prix` (int): Le prix du produit.
    *   `quantite` (int): La quantité du produit.
*   **Raises:**
    *   `ValueError`: Si la quantité est négative.

## Utilisation

Voici un exemple d'utilisation du module :

```python
# Créer des commandes
c1 = Commande("Ali", [("PC", 120000, 1)])
c2 = Commande("Sara", [("Clavier", 3000, 2)])

# Ajouter un produit à une commande (avec gestion d'erreur)
try:
    ajouter_produit_globale(c2, "Souris", 1500, 3)
except ValueError as e:
    print(f"Erreur lors de l'ajout du produit : {e}")

# Calculer le total de toutes les commandes
total_des_commandes = total_commandes([c1, c2])
print(f"Le total de toutes les commandes est : {total_des_commandes}")

# Afficher le total d'une commande individuelle
print(f"Le total de la commande de Sara est : {c2.total()}")
```

## Dépendances
Ce module ne nécessite aucune dépendance externe. Tous les imports proviennent de la bibliothèque standard Python.
```