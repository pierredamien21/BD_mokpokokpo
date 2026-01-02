from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.model import Commande
from schema.commande import CommandeCreate, CommandeOut

router = APIRouter(prefix="/commandes", tags=["Commandes"])

@router.post("/", response_model=CommandeOut)
def create_commande(commande: CommandeCreate, db: Session = Depends(get_db)):
    db_commande = Commande(**commande.model_dump())
    db.add(db_commande)
    db.commit()
    db.refresh(db_commande)
    return db_commande

@router.get("/", response_model=list[CommandeOut])
def get_commandes(db: Session = Depends(get_db)):
    return db.query(Commande).all()
