"""Module de gestion des utilisateurs et de leurs comptes."""

# import copy  # Ligne 3: Unused import copy. Le module 'copy' est importé mais pas utilisé.

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
        # Ligne 174 : Unexpected EOF while parsing. Il manque la fin de
        # l'instruction dans la méthode 'retirer'.
        # Ligne 175 : Final newline missing (Type: pep8_violation, Sévérité: low)


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
    # Ligne 152 : Catching too general exception Exception. Il est préférable de capturer des exceptions plus spécifiques pour une meilleure gestion des erreurs.
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
    except (ValueError, IOError) as e:
        print(f"Une erreur est survenue lors du transfert: {e}")


def afficher_utilisateurs():
    """Affiche les informations de tous les utilisateurs."""
    # Ligne 159 : Unused variable 'i'. La variable 'i' est déclarée mais n'est pas utilisée dans la boucle.
    for _, u in enumerate(UTILISATEURS):
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
# Ligne 182 : Final newline missing (Type: pep8_violation, Sévérité: low)