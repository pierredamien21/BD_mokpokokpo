from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import AlerteStock, Produit
from schema.alerte_stock import AlerteStockCreate, AlerteStockRead

from security.access_control import RoleChecker
from schema.enums import RoleEnum

router = APIRouter(
    prefix="/alertes-stock",
    tags=["Alertes Stock"]
)

@router.post("/", response_model=AlerteStockRead, dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_STOCK]))])
def create_alerte(data: AlerteStockCreate, db: Session = Depends(get_db)):
    if not db.get(Produit, data.id_produit):
        raise HTTPException(status_code=404, detail="Produit introuvable")

    alerte = AlerteStock(**data.model_dump())
    try:
        db.add(alerte)
        db.commit()
        db.refresh(alerte)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erreur lors de la création de l'alerte")
    return alerte

@router.get("/", response_model=list[AlerteStockRead], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_STOCK]))])
def get_alertes(db: Session = Depends(get_db)):
    return db.query(AlerteStock).all()

@router.get("/{id_alerte}", response_model=AlerteStockRead)
def get_alerte(id_alerte: int, db: Session = Depends(get_db)):
    alerte = db.get(AlerteStock, id_alerte)
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return alerte
