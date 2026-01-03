from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.model import Vente
from schema.vente import VenteCreate, VenteRead

router = APIRouter(
    prefix="/ventes",
    tags=["Ventes"]
)

@router.post("/", response_model=VenteRead)
def create_vente(data: VenteCreate, db: Session = Depends(get_db)):
    vente = Vente(**data.model_dump())
    db.add(vente)
    db.commit()
    db.refresh(vente)
    return vente
