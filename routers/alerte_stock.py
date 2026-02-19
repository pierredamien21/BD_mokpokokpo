from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import AlerteStock, Produit, Utilisateur
from schema.alerte_stock import AlerteStockCreate, AlerteStockRead

from security.access_control import RoleChecker
from schema.enums import RoleEnum
from security.dependencies import get_current_user

router = APIRouter(
    prefix="/alertes-stock",
    tags=["Alertes Stock"]
)

@router.post("/", response_model=AlerteStockRead)
def create_alerte(data: AlerteStockCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
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

@router.get("/", response_model=list[AlerteStockRead])
def get_alertes(db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    return db.query(AlerteStock).all()

@router.get("/{id_alerte}", response_model=AlerteStockRead)
def get_alerte(id_alerte: int, db: Session = Depends(get_db)):
    alerte = db.get(AlerteStock, id_alerte)
    if not alerte:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    return alerte
