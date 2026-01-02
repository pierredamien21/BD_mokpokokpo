from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.model import Stock
from schema.stock import StockCreate, StockOut

router = APIRouter(prefix="/stocks", tags=["Stocks"])

@router.post("/", response_model=StockOut)
def create_stock(stock: StockCreate, db: Session = Depends(get_db)):
    db_stock = Stock(**stock.model_dump())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

@router.get("/", response_model=list[StockOut])
def get_stocks(db: Session = Depends(get_db)):
    return db.query(Stock).all()

