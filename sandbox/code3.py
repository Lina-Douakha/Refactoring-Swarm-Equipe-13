"""Gestionnaire de tâches."""


class Tache:
    """Représente une tâche avec un titre et des tags."""

    def __init__(self, titre, tags=None):
        """Initialise une nouvelle instance de Tache.

        Args:
            titre (str): Le titre de la tâche.
            tags (list, optional): Une liste de tags associés à la tâche.
                                   Par défaut, une nouvelle liste vide est créée.
        """
        self.titre = titre
        if tags is None:
            self.tags = []
        else:
            self.tags = tags

    def ajouter_tag(self, tag):
        """Ajoute un tag à la tâche.

        Args:
            tag (str): Le tag à ajouter.
        """
        self.tags.append(tag)


class GestionTaches:
    """Gère une collection de tâches."""

    def __init__(self):
        """Initialise une nouvelle instance de GestionTaches."""
        self.taches = []

    def ajouter(self, tache):
        """Ajoute une tâche à la liste des tâches.

        Args:
            tache (Tache): L'objet Tache à ajouter.
        """
        self.taches.append(tache)

    def supprimer(self, titre):
        """Supprime une tâche de la liste en utilisant son titre.

        Args:
            titre (str): Le titre de la tâche à supprimer.
        """
        taches_a_garder = []
        tache_supprimee = False
        for t in self.taches:
            if t.titre == titre and not tache_supprimee:
                tache_supprimee = True
            else:
                taches_a_garder.append(t)
        self.taches = taches_a_garder

        if tache_supprimee:
            print("Tâche supprimée")

    def afficher(self):
        """Affiche toutes les tâches avec leur titre et leurs tags."""
        for t in self.taches:
            print(t.titre, t.tags)


if __name__ == "__main__":
    t1 = Tache("Réviser", ["python"])
    t2 = Tache("Projet")

    t2.ajouter_tag("urgent")

    g = GestionTaches()
    g.ajouter(t1)
    g.ajouter(t2)

    g.supprimer("Réviser")
    g.afficher()