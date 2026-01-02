from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.model import AlerteStock
from schema.alerte_stock import AlerteStockOut

router = APIRouter(prefix="/alertes-stock", tags=["AlertesStock"])

@router.get("/", response_model=list[AlerteStockOut])
def get_alertes_stock(db: Session = Depends(get_db)):
    return db.query(AlerteStock).all()