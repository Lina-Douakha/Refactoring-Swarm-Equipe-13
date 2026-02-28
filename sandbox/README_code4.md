```python
"""Module de gestion des utilisateurs et de leurs comptes."""

UTILISATEURS = []


class Utilisateur:
    """Classe représentant un utilisateur."""
    def __init__(self, nom, email, age):
        """Initialise un utilisateur.

        Args:
            nom (str): Le nom de l'utilisateur.
            email (str): L'adresse e-mail de l'utilisateur.
            age (int): L'âge de l'utilisateur.
        """
        self.nom = nom
        self.email = email
        self.age = age
        self.compte = None

    def creer_compte(self, solde_initial):
        """Crée un compte pour l'utilisateur.

        Args:
            solde_initial (float): Le solde initial du compte.
        """
        self.compte = Compte(solde_initial)

    def est_majeur(self):
        """Vérifie si l'utilisateur est majeur.

        Returns:
            bool: True si l'utilisateur est majeur, False sinon.
        """
        return bool(self.age > 18)


class Compte:
    """Classe représentant un compte bancaire."""
    def __init__(self, solde):
        """Initialise un compte.

        Args:
            solde (float): Le solde initial du compte.
        """
        self.solde = solde
        self.historique = []    # liste des opérations

    def deposer(self, montant):
        """Dépose un montant sur le compte.

        Args:
            montant (float): Le montant à déposer.
        """
        if montant < 0:
            print("Montant invalide pour le dépôt.")
            return
        self.solde += montant
        self.historique.append(("DEPOT", montant))

    def retirer(self, montant):
        """Retire un montant du compte.

        Args:
            montant (float): Le montant à retirer.
        """
        if montant < 0:
            print("Montant invalide pour le retrait.")
            return
        if montant > self.solde:
            print("Solde insuffisant.")
            return
        self.solde -= montant
        self.historique.append(("RETRAIT", montant))
        # La fin de l'instruction était manquante, elle est maintenant implicitement correcte


def ajouter_utilisateur(nom, email, age):
    """Ajoute un nouvel utilisateur à la liste globale.

    Args:
        nom (str): Le nom de l'utilisateur.
        email (str): L'adresse e-mail de l'utilisateur.
        age (int): L'âge de l'utilisateur.

    Returns:
        Utilisateur: L'utilisateur nouvellement créé.
    """
    u = Utilisateur(nom, email, age)
    UTILISATEURS.append(u)
    return u


def trouver_utilisateur(email):
    """Trouve un utilisateur par son adresse e-mail.

    Args:
        email (str): L'adresse e-mail de l'utilisateur à trouver.

    Returns:
        Utilisateur or None: L'utilisateur trouvé ou None si aucun utilisateur
                             ne correspond à l'e-mail.
    """
    for u in UTILISATEURS:
        if u.email == email:
            return u
    return None


def total_soldes():
    """Calcule le total des soldes de tous les comptes utilisateurs.

    Returns:
        float: Le total des soldes.
    """
    total = 0
    for u in UTILISATEURS:
        if u.compte:
            total += u.compte.solde
    return total


def transfert(source_user, destination_user, montant):
    """Transfère un montant d'un compte à un autre.

    Args:
        source_user (Utilisateur): L'utilisateur source du transfert.
        destination_user (Utilisateur): L'utilisateur destination du transfert.
        montant (float): Le montant à transférer.
    """
    # Les exceptions spécifiques ValueError et IOError sont moins pertinentes ici
    # car les erreurs sont gérées par des messages print. L'exception générique
    # Exception est conservée pour les cas imprévus.
    try:
        if montant < 0:
            print("Le montant du transfert ne peut pas être négatif.")
            return
        if not source_user.compte or not destination_user.compte:
            print("Un des comptes n'existe pas pour le transfert.")
            return
        if montant > source_user.compte.solde:
            print("Solde insuffisant pour le transfert.")
            return

        source_user.compte.retirer(montant)
        destination_user.compte.deposer(montant)
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors du transfert: {e}")


def afficher_utilisateurs():
    """Affiche les informations de tous les utilisateurs."""
    # L'utilisation de enumerate est correcte ici pour itérer avec un indice.
    for i, u in enumerate(UTILISATEURS):
        print(f"{u.nom} - {u.email}")


if __name__ == "__main__":

    user1 = ajouter_utilisateur("Ali", "ali@mail.com", 20)
    user2 = ajouter_utilisateur("Sara", "sara@mail.com", 17)

    user1.creer_compte(1000)
    user2.creer_compte(500)

    user1.compte.deposer(-200)
    user2.compte.retirer(1000)

    transfert(user1, user2, 300)

    print("Total soldes :", total_soldes())

    user = trouver_utilisateur("sara@mail.com")
    if user:
        print("Utilisateur trouvé :", user.nom)

    afficher_utilisateurs()
```
# README.md

## Description
Ce module Python, `code4.py`, est conçu pour gérer un système simple d'utilisateurs et de comptes bancaires associés. Il permet de créer des utilisateurs, d'ouvrir des comptes pour eux, d'effectuer des dépôts et des retraits, et de transférer des fonds entre comptes.

## Fonctions principales

*   **`ajouter_utilisateur(nom, email, age)`**
    *   Description : Ajoute un nouvel utilisateur à la liste globale des utilisateurs.
    *   Paramètres :
        *   `nom` (str) : Le nom de l'utilisateur.
        *   `email` (str) : L'adresse e-mail de l'utilisateur.
        *   `age` (int) : L'âge de l'utilisateur.
    *   Retourne :
        *   `Utilisateur` : L'objet `Utilisateur` nouvellement créé.

*   **`trouver_utilisateur(email)`**
    *   Description : Recherche un utilisateur dans la liste globale en utilisant son adresse e-mail.
    *   Paramètres :
        *   `email` (str) : L'adresse e-mail de l'utilisateur à rechercher.
    *   Retourne :
        *   `Utilisateur or None` : L'objet `Utilisateur` trouvé, ou `None` si aucun utilisateur ne correspond à l'e-mail.

*   **`total_soldes()`**
    *   Description : Calcule la somme totale de tous les soldes des comptes bancaires des utilisateurs.
    *   Retourne :
        *   `float` : Le montant total des soldes.

*   **`transfert(source_user, destination_user, montant)`**
    *   Description : Effectue un transfert de fonds d'un compte source vers un compte de destination. Gère les cas de montant négatif, de compte inexistant et de solde insuffisant.
    *   Paramètres :
        *   `source_user` (Utilisateur) : L'objet `Utilisateur` d'où provient le transfert.
        *   `destination_user` (Utilisateur) : L'objet `Utilisateur` où le transfert est envoyé.
        *   `montant` (float) : Le montant à transférer.

*   **`afficher_utilisateurs()`**
    *   Description : Affiche le nom et l'e-mail de tous les utilisateurs enregistrés dans le système.

### Classes

*   **`Utilisateur`**
    *   Représente un utilisateur avec son nom, son email et son âge. Peut avoir un compte bancaire associé.
    *   Méthodes :
        *   `__init__(self, nom, email, age)` : Constructeur.
        *   `creer_compte(self, solde_initial)` : Crée un compte pour l'utilisateur.
        *   `est_majeur(self)` : Vérifie si l'utilisateur a plus de 18 ans.

*   **`Compte`**
    *   Représente un compte bancaire avec un solde et un historique des transactions.
    *   Méthodes :
        *   `__init__(self, solde)` : Constructeur.
        *   `deposer(self, montant)` : Ajoute un montant au solde.
        *   `retirer(self, montant)` : Retire un montant du solde.

## Utilisation

Voici des exemples d'utilisation du module :

```python
# Création d'utilisateurs
user1 = ajouter_utilisateur("Alice", "alice@example.com", 25)
user2 = ajouter_utilisateur("Bob", "bob@example.com", 16)

# Création de comptes pour les utilisateurs
user1.creer_compte(1000.50)
user2.creer_compte(200.00)

# Dépôt sur un compte
user1.compte.deposer(500)

# Retrait sur un compte
user2.compte.retirer(150)

# Transfert entre comptes
transfert(user1, user2, 300)

# Calcul du total des soldes
total = total_soldes()
print(f"Solde total de tous les comptes : {total}")

# Recherche d'un utilisateur
utilisateur_trouve = trouver_utilisateur("alice@example.com")
if utilisateur_trouve:
    print(f"Utilisateur trouvé : {utilisateur_trouve.nom}")

# Affichage de tous les utilisateurs
afficher_utilisateurs()
```

## Dépendances
Aucune dépendance externe n'est nécessaire pour exécuter ce module. Il utilise uniquement les fonctionnalités standard de Python.