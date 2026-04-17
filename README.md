# API Compte de Banque Monopoly

Cette API permet de gérer des comptes de joueurs pour une banque Monopoly.

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

## Authentification FranceConnect (MVP SSO)

Cette API peut exiger un token FranceConnect sur tous les endpoints métier.

Variables d'environnement:

- `SERVICE_AUTH_ENABLED=true` pour activer le contrôle d'auth
- `FRANCECONNECT_BASE_URL=http://127.0.0.1:8000`
- `AUTH_REQUEST_TIMEOUT_SECONDS=2.5`

Comportement:

- `/health` reste public
- `/comptes*` et `/transferts` exigent `Authorization: Bearer <token>`
- token invalide/manquant -> `401`
- fournisseur d'auth indisponible -> `503`
