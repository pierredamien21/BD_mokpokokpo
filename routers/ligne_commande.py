from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import LigneCommande, Commande, Produit
from schema.ligne_commande import LigneCommandeCreate, LigneCommandeRead

from security.access_control import RoleChecker
from schema.enums import RoleEnum

router = APIRouter(
    prefix="/ligne-commandes",
    tags=["Lignes Commande"]
)

@router.post("/", response_model=LigneCommandeRead, dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.CLIENT]))])
def create_ligne_commande(data: LigneCommandeCreate, db: Session = Depends(get_db)):
    # Vérifications existence
    if not db.get(Commande, data.id_commande):
        raise HTTPException(status_code=404, detail="Commande introuvable")
    if not db.get(Produit, data.id_produit):
        raise HTTPException(status_code=404, detail="Produit introuvable")

    ligne = LigneCommande(**data.model_dump())
    try:
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ligne de commande déjà existante pour ce produit")
    return ligne

@router.get("/", response_model=list[LigneCommandeRead], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL, RoleEnum.GEST_STOCK]))])
def get_lignes_commande(db: Session = Depends(get_db)):
    return db.query(LigneCommande).all()

@router.get("/{id_ligne}", response_model=LigneCommandeRead)
def get_ligne_commande(id_ligne: int, db: Session = Depends(get_db)):
    ligne = db.get(LigneCommande, id_ligne)
    if not ligne:
        raise HTTPException(status_code=404, detail="Ligne de commande introuvable")
    return ligne
