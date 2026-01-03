from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import Stock, Produit
from schema.stock import StockCreate, StockRead
from security.access_control import RoleChecker
from schema.enums import RoleEnum

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)

@router.post("/", response_model=StockRead, dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_STOCK]))])
def create_stock(data: StockCreate, db: Session = Depends(get_db)):
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

@router.get("/", response_model=list[StockRead], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_STOCK, RoleEnum.GEST_COMMERCIAL]))])
def get_stocks(db: Session = Depends(get_db)):
    return db.query(Stock).all()
