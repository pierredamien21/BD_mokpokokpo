from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.model import AlerteStock
from schema.alerte_stock import AlerteStockCreate, AlerteStockRead

router = APIRouter(
    prefix="/alertes-stock",
    tags=["Alertes Stock"]
)

@router.post("/", response_model=AlerteStockRead)
def create_alerte(data: AlerteStockCreate, db: Session = Depends(get_db)):
    alerte = AlerteStock(**data.model_dump())
    db.add(alerte)
    db.commit()
    db.refresh(alerte)
    return alerte

@router.get("/", response_model=list[AlerteStockRead])
def get_alertes(db: Session = Depends(get_db)):
    return db.query(AlerteStock).all()
