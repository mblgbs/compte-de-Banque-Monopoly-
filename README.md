# API Compte de Banque Monopoly

Cette API permet de gérer des comptes de joueurs pour une banque Monopoly.

**Écosystème :** découverte centralisée des URLs — `GET http://127.0.0.1:8004/ecosystem` ([services-Monopoly- README](../services-Monopoly-/README.md#decouverte-des-services-ecosystem)) ; la banque est en `8002` dans le runbook local.

## Lancer l'API

```bash
python api.py
```

Serveur par défaut: `http://0.0.0.0:8000`

## Endpoints

### Vérification santé
- `GET /health`

### Comptes
- `POST /comptes`
  - body: `{ "nom": "Alice", "solde_initial": 1500 }`
- `GET /comptes`
- `GET /comptes/{id}`
- `POST /comptes/{id}/depot`
  - body: `{ "montant": 200 }`
- `POST /comptes/{id}/retrait`
  - body: `{ "montant": 100 }`

### Transfert
- `POST /transferts`
  - body: `{ "source_id": 1, "destination_id": 2, "montant": 300 }`

## Exemples curl

```bash
curl -X POST http://localhost:8000/comptes \
  -H 'Content-Type: application/json' \
  -d '{"nom":"Alice","solde_initial":1500}'

curl -X POST http://localhost:8000/comptes/1/depot \
  -H 'Content-Type: application/json' \
  -d '{"montant":200}'

curl -X POST http://localhost:8000/transferts \
  -H 'Content-Type: application/json' \
  -d '{"source_id":1,"destination_id":2,"montant":100}'
```

## Tests

```bash
python -m unittest discover -s tests -v
```
