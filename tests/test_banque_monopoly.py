import unittest

from banque_monopoly import BanqueMonopoly, CompteIntrouvableError, SoldeInsuffisantError


class TestBanqueMonopoly(unittest.TestCase):
    def setUp(self) -> None:
        self.banque = BanqueMonopoly()

    def test_creer_compte(self):
        compte = self.banque.creer_compte("Alice", 1500)
        self.assertEqual(compte.id_compte, 1)
        self.assertEqual(compte.solde, 1500)

    def test_depot_retrait(self):
        compte = self.banque.creer_compte("Bob", 1000)
        self.banque.depot(compte.id_compte, 200)
        self.assertEqual(self.banque.obtenir_compte(compte.id_compte).solde, 1200)
        self.banque.retrait(compte.id_compte, 300)
        self.assertEqual(self.banque.obtenir_compte(compte.id_compte).solde, 900)

    def test_transfert(self):
        a = self.banque.creer_compte("A", 1000)
        b = self.banque.creer_compte("B", 1000)
        self.banque.transfert(a.id_compte, b.id_compte, 250)
        self.assertEqual(self.banque.obtenir_compte(a.id_compte).solde, 750)
        self.assertEqual(self.banque.obtenir_compte(b.id_compte).solde, 1250)

    def test_compte_introuvable(self):
        with self.assertRaises(CompteIntrouvableError):
            self.banque.obtenir_compte(999)

    def test_solde_insuffisant(self):
        c = self.banque.creer_compte("C", 10)
        with self.assertRaises(SoldeInsuffisantError):
            self.banque.retrait(c.id_compte, 99)


if __name__ == "__main__":
    unittest.main()
