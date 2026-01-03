from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.model import Commande
from schema.commande import CommandeCreate, CommandeRead

router = APIRouter(
    prefix="/commandes",
    tags=["Commandes"]
)

@router.post("/", response_model=CommandeRead)
def create_commande(data: CommandeCreate, db: Session = Depends(get_db)):
    commande = Commande(**data.model_dump())
    db.add(commande)
    db.commit()
    db.refresh(commande)
    return commande

@router.get("/", response_model=list[CommandeRead])
def get_commandes(db: Session = Depends(get_db)):
    return db.query(Commande).all()
