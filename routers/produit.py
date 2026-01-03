from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.model import Produit
from schema.produit import ProduitCreate, ProduitRead

router = APIRouter(
    prefix="/produits",
    tags=["Produits"]
)

@router.post("/", response_model=ProduitRead)
def create_produit(data: ProduitCreate, db: Session = Depends(get_db)):
    produit = Produit(**data.model_dump())
    db.add(produit)
    db.commit()
    db.refresh(produit)
    return produit

@router.get("/", response_model=list[ProduitRead])
def get_produits(db: Session = Depends(get_db)):
    return db.query(Produit).all()
