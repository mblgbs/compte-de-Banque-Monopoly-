# Compte de Banque Monopoly

Ce dépôt contient une implémentation simple d'un **compte de banque Monopoly** en Python.

## Fonctionnalités

- Création de comptes joueurs avec un solde initial.
- Dépôts et retraits.
- Transferts entre joueurs.
- Versement d'argent de la banque vers un joueur.
- Encaissement d'argent d'un joueur vers la banque.

## Utilisation rapide

```python
from monopoly_bank import BanqueMonopoly

banque = BanqueMonopoly(solde_banque=100000)
banque.creer_compte("Alice")
banque.creer_compte("Bob", solde_initial=1200)

banque.verser_depuis_banque("Alice", 1500)
banque.transferer("Alice", "Bob", 200)

print(banque.solde("Alice"))
print(banque.solde("Bob"))
print(banque.solde_banque)
```

## Lancer les tests

```bash
python -m unittest -v
```
