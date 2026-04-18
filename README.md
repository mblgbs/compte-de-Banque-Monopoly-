# API Compte de Banque Monopoly

Cette API permet de gérer des comptes de joueurs pour une banque Monopoly.

## Lancer l'API

```bash
python api.py
```

Serveur par défaut: `http://0.0.0.0:8002`

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
curl -X POST http://localhost:8002/comptes \
  -H 'Content-Type: application/json' \
  -d '{"nom":"Alice","solde_initial":1500}'

curl -X POST http://localhost:8002/comptes/1/depot \
  -H 'Content-Type: application/json' \
  -d '{"montant":200}'

curl -X POST http://localhost:8002/transferts \
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
- `FRANCECONNECT_BASE_URL=http://127.0.0.1:8001`
- `AUTH_REQUEST_TIMEOUT_SECONDS=2.5`

Comportement:

- `/health` reste public
- `/comptes*` et `/transferts` exigent `Authorization: Bearer <token>`
- token invalide/manquant -> `401`
- fournisseur d'auth indisponible -> `503`

## Sauvegarde centralisee (save-service + PostgreSQL)

L'API bancaire charge l'etat au demarrage depuis `save-service` et persiste
automatiquement apres:
- creation de compte,
- depot,
- retrait,
- transfert.

En cas d'indisponibilite du service, l'API continue en memoire (fallback).

Variables d'environnement:

- `SAVE_SERVICE_BASE_URL=http://127.0.0.1:8010`
- `SAVE_SERVICE_TIMEOUT_SECONDS=2.5`
- `SAVE_SERVICE_RETRIES=1`
- `SAVE_SERVICE_API_TOKEN=` (optionnel)

## Guide d'integration avec Web et Declaration

Cette API est la source de verite des soldes. Les applications clientes gardent leurs IDs locaux, mais utilisent les IDs de comptes de la banque pour les mouvements d'argent.

### 1) Preparer les services

Demarrer la banque:

```bash
cd compte-de-Banque-Monopoly-
python api.py
```

Demarrer Web Monopoly (connecte a la banque):

```bash
cd Web-monopoly-
set BANK_API_BASE_URL=http://127.0.0.1:8002
set BANK_REQUEST_TIMEOUT_MS=2500
npm install
npm start
```

Demarrer Declaration Monopoly (connecte a la banque):

```bash
cd D-claration-Monopoly-
set BANK_API_BASE_URL=http://127.0.0.1:8002
python api.py
```

### 2) Sequence Web -> Banque

1. Un joueur rejoint une salle (`join-room` ou `POST /api/rooms/{code}/join`).
2. Web cree un compte banque via `POST /comptes` et stocke le mapping `playerId -> accountId`.
3. Un transfert en salle appelle `POST /transferts` sur la banque.
4. Les soldes retournes par la banque sont reinjectes dans l'etat de la salle et diffuses aux clients.

Exemple de transfert banque:

```bash
curl -X POST http://127.0.0.1:8002/transferts \
  -H "Content-Type: application/json" \
  -d "{\"source_id\":1,\"destination_id\":2,\"montant\":100}"
```

### 3) Sequence Declaration -> Banque

1. Le front Declaration envoie une declaration a `POST /declarations` de `D-claration-Monopoly-/api.py`.
2. Le service Declaration cree (si besoin) le compte du joueur en banque.
3. Le montant est applique en banque:
   - montant positif -> `POST /comptes/{id}/retrait`
   - montant negatif -> `POST /comptes/{id}/depot`
4. La reponse retourne l'entree et le solde courant du joueur.

Exemple `fetch` depuis le front:

```js
await fetch("http://127.0.0.1:8003/declarations", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    joueur: "Marie",
    type: "impot",
    evenement: "Taxe de luxe",
    montant: 100,
    notes: "Paiement tour 3"
  })
});
```

### Erreurs frequentes

- `400` "Solde insuffisant": retrait superieur au solde du compte source.
- `400` "Compte introuvable": accountId invalide ou mapping local obsolete.
- `401`: auth activee et token manquant/invalide.
- `503` "Auth provider unavailable": service FranceConnect indisponible.
- `503` "Service bancaire indisponible": application cliente ne peut pas joindre la banque.
