from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import Stock, Produit
from schema.stock import StockCreate, StockRead

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)

@router.post("/", response_model=StockRead)
def create_stock(data: StockCreate, db: Session = Depends(get_db)):
    produit = db.query(Produit).get(data.id_produit)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit inexistant")

    stock = Stock(**data.model_dump())
    db.add(stock)
    db.commit()
    db.refresh(stock)
    return stock

@router.get("/", response_model=list[StockRead])
def get_stocks(db: Session = Depends(get_db)):
    return db.query(Stock).all()
