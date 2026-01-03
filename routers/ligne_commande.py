from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.model import LigneCommande
from schema.ligne_commande import LigneCommandeCreate, LigneCommandeRead

router = APIRouter(
    prefix="/ligne-commandes",
    tags=["Lignes Commande"]
)

@router.post("/", response_model=LigneCommandeRead)
def create_ligne_commande(data: LigneCommandeCreate, db: Session = Depends(get_db)):
    ligne = LigneCommande(**data.model_dump())
    db.add(ligne)
    db.commit()
    db.refresh(ligne)
    return ligne
