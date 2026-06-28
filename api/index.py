import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from banque_monopoly import BanqueMonopoly, CompteIntrouvableError, SoldeInsuffisantError, compte_en_dict

app = FastAPI(title="Compte de Banque Monopoly API")
banque = BanqueMonopoly()

class CreateCompteBody(BaseModel):
    nom: str
    solde_initial: int = 1500

class MontantBody(BaseModel):
    montant: int

class TransfertBody(BaseModel):
    source_id: int
    destination_id: int
    montant: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {"message": "Compte de Banque Monopoly API"}

@app.get("/comptes")
def lister_comptes():
    return {"comptes": [compte_en_dict(c) for c in banque.lister_comptes()]}

@app.get("/comptes/{compte_id}")
def obtenir_compte(compte_id: int):
    try:
        return compte_en_dict(banque.obtenir_compte(compte_id))
    except CompteIntrouvableError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/comptes", status_code=201)
def creer_compte(body: CreateCompteBody):
    compte = banque.creer_compte(body.nom, body.solde_initial)
    return compte_en_dict(compte)

@app.post("/comptes/{compte_id}/depot")
def depot(compte_id: int, body: MontantBody):
    try:
        return compte_en_dict(banque.depot(compte_id, body.montant))
    except CompteIntrouvableError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/comptes/{compte_id}/retrait")
def retrait(compte_id: int, body: MontantBody):
    try:
        return compte_en_dict(banque.retrait(compte_id, body.montant))
    except (CompteIntrouvableError, SoldeInsuffisantError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/transferts")
def transfert(body: TransfertBody):
    try:
        banque.transfert(body.source_id, body.destination_id, body.montant)
        return {
            "message": "Transfert effectue",
            "source": compte_en_dict(banque.obtenir_compte(body.source_id)),
            "destination": compte_en_dict(banque.obtenir_compte(body.destination_id)),
        }
    except (CompteIntrouvableError, SoldeInsuffisantError) as e:
        raise HTTPException(status_code=400, detail=str(e))
