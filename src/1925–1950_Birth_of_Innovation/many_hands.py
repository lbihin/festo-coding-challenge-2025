from copy import deepcopy
from enum import Enum
from typing import List, Tuple


class Noeud:

    def __init__(self, origine, destination, temps_trajet):
        self.origine = origine
        self.destination = destination
        self.temps_trajet = temps_trajet
        self.lettre = None

    def __str__(self):
        return f"{self.origine} -> {self.destination} [travel-time={self.temps_trajet} hrs]"

    def __repr__(self):
        return self.__str__()

    @classmethod
    def from_string(cls, line: str):
        parts = line.strip().split()
        return cls(parts[1], parts[3], float(parts[5]))


def lister_les_connections():
    for line in lines:
        Connections.parse_connection(line)


class Connections:
    registre = {}

    @classmethod
    def parse_connection(cls, line: str):
        connection = Noeud.from_string(line)
        cls.enregister(connection)

    @classmethod
    def enregister(cls, connection):
        cls.registre.setdefault(connection.origine, []).append(connection)

    @classmethod
    def prochaine_destination(cls, origine: str) -> List[Noeud]:
        return cls.registre.get(origine, [])


class Chemin:
    compteur = 0
    registre = {}

    def __init__(self):
        self.pk = Chemin.compteur
        Chemin.compteur += 1
        self.origine = "S"
        self.destination = "E"
        self.etapes = []
        self._temps_total = 0.0
        self.lettres = []
        self.actif = True
        self.derniere_etape = None

    @classmethod
    def obtenir_chemins_complets(cls, ascending=True) -> List["Chemin"]:
        chemins = [
            chemin
            for chemin in cls.registre.values()
            if chemin.derniere_etape == chemin.destination
        ]
        return sorted(chemins, reverse=not ascending)

    @classmethod
    def obtenir_les_chemins_actifs(cls) -> List["Chemin"]:
        return [chemin for chemin in cls.registre.values() if chemin.actif]

    @classmethod
    def obtenir_les_chemins_definitifs(cls) -> List["Chemin"]:
        return [chemin for chemin in cls.registre.values() if not chemin.actif]

    @classmethod
    def ajouter_chemin(cls):
        chemin = cls()
        cls.registre[chemin.pk] = chemin
        return chemin

    @classmethod
    def dupliquer_chemin(cls, pk: int):
        obj = cls.registre.get(pk)
        if not obj:
            raise ValueError(f"Chemin avec pk {pk} n'existe pas.")

        new_ = cls.ajouter_chemin()
        new_.etapes = deepcopy(obj.etapes)
        new_._temps_total = obj._temps_total
        new_.lettres = deepcopy(obj.lettres)
        return new_

    def ajouter_etape(self, connection: Noeud):
        if self.actif:
            # Arrêter si le chemin boucle sur lui-même
            if connection.destination in self.etapes:
                self.actif = False
                return
            self.etapes.append(connection.destination)
            self._temps_total += connection.temps_trajet
            if connection.lettre:
                self.lettres.append(connection.lettre)
            self.derniere_etape = connection.destination

            # Désactiver si la destination finale est atteinte
            if connection.destination == self.destination:
                self.actif = False

    @staticmethod
    def ajouter_noeud(chemin: "Chemin"):
        try:
            destinations_suivantes = Connections.prochaine_destination(
                chemin.etapes[-1]
            )
        except IndexError:
            destinations_suivantes = Connections.prochaine_destination(chemin.origine)

        for cnt, destination in enumerate(destinations_suivantes):
            if len(destinations_suivantes) == 1:
                chemin.ajouter_etape(destination)
                continue
            if cnt // (len(destinations_suivantes) - 1) == 1:
                chemin.ajouter_etape(destination)
            else:
                new_chemin = Chemin.dupliquer_chemin(chemin.pk)
                new_chemin.ajouter_etape(destination)

    def __eq__(self, other):
        if not isinstance(other, Chemin):
            return NotImplemented
        return self._temps_total == other._temps_total

    def __lt__(self, other):
        if not isinstance(other, Chemin):
            return NotImplemented
        return self._temps_total < other._temps_total

    def __le__(self, other):
        if not isinstance(other, Chemin):
            return NotImplemented
        return self._temps_total <= other._temps_total


class Planificateur:
    Chemin.ajouter_chemin()

    @classmethod
    def construire_tous_les_chemins(cls):

        while chemins_actifs := Chemin.obtenir_les_chemins_actifs():
            # nouveaux_chemins = []
            for chemin in chemins_actifs:
                Chemin.ajouter_noeud(chemin)
        return Chemin.obtenir_les_chemins_definitifs()

    @staticmethod
    def afficher_chemin_le_plus_rapide() -> Tuple[Chemin, float]:
        # Trier les chemins par temps total
        chemins = Chemin.obtenir_chemins_complets(ascending=True)
        chemin_rapide = chemins[0]
        return chemin_rapide, chemin_rapide._temps_total


if __name__ == "__main__":
    with open("connections.txt", "r") as f:
        lines = f.readlines()[2:]

    lister_les_connections()
    plannificateur = Planificateur()
    plannificateur.construire_tous_les_chemins()

    print("Chemins construits:")

    for chemin in Chemin.obtenir_chemins_complets():
        print(
            f"Chemin {chemin.pk}: {' -> '.join(chemin.etapes)} | Temps total: {chemin._temps_total} hrs"
        )

    chemin_rapide, temps = plannificateur.afficher_chemin_le_plus_rapide()
    print(
        f"Chemin le plus rapide: {' -> '.join(chemin_rapide.etapes)} | Temps total: {temps} hrs"
    )

    mapping = {
        "A": None,
        "B": "H",
        "C": None,
        "D": "A",
        "E": "S",
        "F": "N",
        "G": "D",
        "H": None,
        "I": None,
        "J": None,
        "K": None,
    }
    nom = "".join(
        filter(
            None, map(lambda lettre: mapping.get(lettre) or "", chemin_rapide.etapes)
        )
    )
    print(f"Nom à trouver: {nom}")
