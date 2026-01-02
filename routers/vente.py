from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.model import Vente
from schema.vente import VenteCreate, VenteOut

router = APIRouter(prefix="/ventes", tags=["Ventes"])

@router.post("/", response_model=VenteOut)
def create_vente(vente: VenteCreate, db: Session = Depends(get_db)):
    db_vente = Vente(**vente.model_dump())
    db.add(db_vente)
    db.commit()
    db.refresh(db_vente)
    return db_vente

@router.get("/", response_model=list[VenteOut])
def get_ventes(db: Session = Depends(get_db)):
    return db.query(Vente).all()

