import unittest

from monopoly_bank import BanqueMonopoly, CompteIntrouvableError, SoldeInsuffisantError


class TestBanqueMonopoly(unittest.TestCase):
    def test_creation_de_compte(self):
        banque = BanqueMonopoly(solde_banque=10000)
        banque.creer_compte("Alice", solde_initial=1500)

        self.assertEqual(banque.solde("Alice"), 1500)

    def test_transferer(self):
        banque = BanqueMonopoly()
        banque.creer_compte("Alice", 2000)
        banque.creer_compte("Bob", 1000)

        banque.transferer("Alice", "Bob", 500)

        self.assertEqual(banque.solde("Alice"), 1500)
        self.assertEqual(banque.solde("Bob"), 1500)

    def test_versement_depuis_banque(self):
        banque = BanqueMonopoly(solde_banque=5000)
        banque.creer_compte("Alice", 1000)

        banque.verser_depuis_banque("Alice", 300)

        self.assertEqual(banque.solde("Alice"), 1300)
        self.assertEqual(banque.solde_banque, 4700)

    def test_erreur_compte_introuvable(self):
        banque = BanqueMonopoly()
        with self.assertRaises(CompteIntrouvableError):
            banque.deposer("Alice", 100)

    def test_erreur_solde_insuffisant(self):
        banque = BanqueMonopoly(solde_banque=100)
        banque.creer_compte("Alice", 50)

        with self.assertRaises(SoldeInsuffisantError):
            banque.retirer("Alice", 200)

        with self.assertRaises(SoldeInsuffisantError):
            banque.verser_depuis_banque("Alice", 300)


if __name__ == "__main__":
    unittest.main()
