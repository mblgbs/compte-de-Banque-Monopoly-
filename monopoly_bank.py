"""Gestion simple d'un compte de banque au Monopoly."""

from dataclasses import dataclass, field


class CompteIntrouvableError(KeyError):
    """Le compte demandé n'existe pas."""


class SoldeInsuffisantError(ValueError):
    """Le solde est insuffisant pour réaliser l'opération."""


@dataclass
class BanqueMonopoly:
    """Banque Monopoly avec comptes joueurs et trésorerie centrale."""

    solde_banque: int = 0
    comptes: dict[str, int] = field(default_factory=dict)

    def creer_compte(self, joueur: str, solde_initial: int = 0) -> None:
        """Crée un compte joueur s'il n'existe pas encore."""
        if solde_initial < 0:
            raise ValueError("Le solde initial doit être positif ou nul.")
        if joueur in self.comptes:
            raise ValueError(f"Le compte '{joueur}' existe déjà.")

        self.comptes[joueur] = solde_initial

    def solde(self, joueur: str) -> int:
        """Retourne le solde d'un joueur."""
        self._verifier_compte(joueur)
        return self.comptes[joueur]

    def deposer(self, joueur: str, montant: int) -> None:
        """Ajoute un montant au compte d'un joueur."""
        self._verifier_montant(montant)
        self._verifier_compte(joueur)
        self.comptes[joueur] += montant

    def retirer(self, joueur: str, montant: int) -> None:
        """Retire un montant du compte d'un joueur."""
        self._verifier_montant(montant)
        self._verifier_compte(joueur)

        if self.comptes[joueur] < montant:
            raise SoldeInsuffisantError(
                f"Solde insuffisant pour '{joueur}' (solde={self.comptes[joueur]}, montant={montant})."
            )

        self.comptes[joueur] -= montant

    def transferer(self, source: str, destination: str, montant: int) -> None:
        """Transfère un montant entre deux comptes joueurs."""
        self._verifier_compte(source)
        self._verifier_compte(destination)
        self.retirer(source, montant)
        self.deposer(destination, montant)

    def verser_depuis_banque(self, joueur: str, montant: int) -> None:
        """Verse un montant depuis la banque vers un joueur."""
        self._verifier_montant(montant)
        self._verifier_compte(joueur)

        if self.solde_banque < montant:
            raise SoldeInsuffisantError(
                f"Solde banque insuffisant (solde={self.solde_banque}, montant={montant})."
            )

        self.solde_banque -= montant
        self.comptes[joueur] += montant

    def encaisser_vers_banque(self, joueur: str, montant: int) -> None:
        """Encaisse un montant depuis un joueur vers la banque."""
        self._verifier_montant(montant)
        self._verifier_compte(joueur)
        self.retirer(joueur, montant)
        self.solde_banque += montant

    def _verifier_compte(self, joueur: str) -> None:
        if joueur not in self.comptes:
            raise CompteIntrouvableError(f"Compte introuvable: '{joueur}'.")

    @staticmethod
    def _verifier_montant(montant: int) -> None:
        if montant <= 0:
            raise ValueError("Le montant doit être strictement positif.")
