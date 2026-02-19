from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import Stock, Produit, Utilisateur
from schema.stock import StockCreate, StockRead
from security.access_control import RoleChecker
from schema.enums import RoleEnum
from security.dependencies import get_current_user

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)

@router.post("/", response_model=StockRead)
def create_stock(data: StockCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    produit = db.get(Produit, data.id_produit)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit inexistant")

    stock = Stock(**data.model_dump())
    try:
        db.add(stock)
        db.commit()
        db.refresh(stock)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Stock déjà existant pour ce produit")
    return stock

@router.get("/", response_model=list[StockRead])
def get_stocks(db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    return db.query(Stock).all()
