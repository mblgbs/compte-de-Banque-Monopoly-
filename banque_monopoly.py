from __future__ import annotations

from dataclasses import dataclass


class CompteIntrouvableError(Exception):
    """Raised when an account id does not exist."""


class SoldeInsuffisantError(Exception):
    """Raised when balance is too low for an operation."""


@dataclass
class Compte:
    id_compte: int
    nom: str
    solde: int


class BanqueMonopoly:
    """Bank engine for Monopoly account operations."""

    def __init__(self) -> None:
        self._prochain_id = 1
        self._comptes: dict[int, Compte] = {}

    def creer_compte(self, nom: str, solde_initial: int = 1500) -> Compte:
        if solde_initial < 0:
            raise ValueError("Le solde initial doit être >= 0")

        compte = Compte(id_compte=self._prochain_id, nom=nom, solde=solde_initial)
        self._comptes[self._prochain_id] = compte
        self._prochain_id += 1
        return compte

    def lister_comptes(self) -> list[Compte]:
        return list(self._comptes.values())

    def obtenir_compte(self, id_compte: int) -> Compte:
        compte = self._comptes.get(id_compte)
        if compte is None:
            raise CompteIntrouvableError(f"Compte {id_compte} introuvable")
        return compte

    def depot(self, id_compte: int, montant: int) -> Compte:
        if montant <= 0:
            raise ValueError("Le montant doit être > 0")
        compte = self.obtenir_compte(id_compte)
        compte.solde += montant
        return compte

    def retrait(self, id_compte: int, montant: int) -> Compte:
        if montant <= 0:
            raise ValueError("Le montant doit être > 0")
        compte = self.obtenir_compte(id_compte)
        if compte.solde < montant:
            raise SoldeInsuffisantError("Solde insuffisant")
        compte.solde -= montant
        return compte

    def transfert(self, source_id: int, destination_id: int, montant: int) -> None:
        if source_id == destination_id:
            raise ValueError("Les comptes source et destination doivent être différents")
        self.retrait(source_id, montant)
        self.depot(destination_id, montant)


def compte_en_dict(compte: Compte) -> dict[str, int | str]:
    return {
        "id": compte.id_compte,
        "nom": compte.nom,
        "solde": compte.solde,
    }
