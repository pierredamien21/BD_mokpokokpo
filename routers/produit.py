from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.model import Produit
from schema.produit import ProduitCreate, ProduitOut

router = APIRouter(prefix="/produits", tags=["Produits"])

@router.post("/", response_model=ProduitOut)
def create_produit(produit: ProduitCreate, db: Session = Depends(get_db)):
    db_produit = Produit(**produit.model_dump())
    db.add(db_produit)
    db.commit()
    db.refresh(db_produit)
    return db_produit

@router.get("/", response_model=list[ProduitOut])
def get_produits(db: Session = Depends(get_db)):
    return db.query(Produit).all()