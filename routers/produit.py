from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import Produit, Utilisateur
from schema.produit import ProduitCreate, ProduitRead
from security.access_control import RoleChecker
from schema.enums import RoleEnum
from security.dependencies import get_current_user

router = APIRouter(
    prefix="/produits",
    tags=["Produits"]
)

@router.post("/", response_model=ProduitRead)
def create_produit(data: ProduitCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    produit = Produit(**data.model_dump())
    try:
        db.add(produit)
        db.commit()
        db.refresh(produit)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erreur lors de la création du produit")
    return produit

@router.get("/", response_model=list[ProduitRead])
def get_produits(db: Session = Depends(get_db)):
    return db.query(Produit).all()

@router.get("/{id_produit}", response_model=ProduitRead)
def get_produit(id_produit: int, db: Session = Depends(get_db)):
    produit = db.get(Produit, id_produit)
    if not produit:
        raise HTTPException(status_code=404, detail="Produit non trouvé")
    return produit
