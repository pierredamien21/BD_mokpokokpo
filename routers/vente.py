from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import Vente, Commande
from schema.vente import VenteCreate, VenteRead

from security.access_control import RoleChecker
from schema.enums import RoleEnum

router = APIRouter(
    prefix="/ventes",
    tags=["Ventes"]
)

@router.post("/", response_model=VenteRead, dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]))])
def create_vente(data: VenteCreate, db: Session = Depends(get_db)):
    commande = db.get(Commande, data.id_commande)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    vente = Vente(**data.model_dump())
    try:
        db.add(vente)
        db.commit()
        db.refresh(vente)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Vente déjà enregistrée pour cette commande")
    return vente

@router.get("/", response_model=list[VenteRead], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]))])
def get_ventes(db: Session = Depends(get_db)):
    return db.query(Vente).all()

@router.get("/{id_vente}", response_model=VenteRead)
def get_vente(id_vente: int, db: Session = Depends(get_db)):
    vente = db.get(Vente, id_vente)
    if not vente:
        raise HTTPException(status_code=404, detail="Vente non trouvée")
    return vente
