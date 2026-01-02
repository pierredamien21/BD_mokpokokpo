from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.model import LigneCommande
from schema.ligne_commande import LigneCommandeCreate, LigneCommandeOut

router = APIRouter(prefix="/lignes-commandes", tags=["LignesCommandes"])

@router.post("/", response_model=LigneCommandeOut)
def create_ligne_commande(ligne: LigneCommandeCreate, db: Session = Depends(get_db)):
    db_ligne = LigneCommande(**ligne.model_dump())
    db.add(db_ligne)
    db.commit()
    db.refresh(db_ligne)
    return db_ligne

@router.get("/", response_model=list[LigneCommandeOut])
def get_lignes_commandes(db: Session = Depends(get_db)):
    return db.query(LigneCommande).all()

