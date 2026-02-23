from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import LigneCommande, Commande, Produit, Utilisateur
from schema.ligne_commande import LigneCommandeCreate, LigneCommandeRead

from security.access_control import RoleChecker
from schema.enums import RoleEnum
from security.dependencies import get_current_user

router = APIRouter(
    prefix="/ligne-commandes",
    tags=["Lignes Commande"]
)

@router.post("/", response_model=LigneCommandeRead)
def create_ligne_commande(data: LigneCommandeCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.CLIENT]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
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

@router.get("/", response_model=list[LigneCommandeRead])
def get_lignes_commande(db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL, RoleEnum.GEST_STOCK]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    return db.query(LigneCommande).all()

@router.get("/{id_ligne}", response_model=LigneCommandeRead)
def get_ligne_commande(id_ligne: int, db: Session = Depends(get_db)):
    ligne = db.get(LigneCommande, id_ligne)
    if not ligne:
        raise HTTPException(status_code=404, detail="Ligne de commande introuvable")
    return ligne

@router.delete("/{id_ligne}")
def delete_ligne_commande(id_ligne: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.CLIENT]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    ligne = db.get(LigneCommande, id_ligne)
    if not ligne:
        raise HTTPException(status_code=404, detail="Ligne de commande introuvable")
    try:
        db.delete(ligne)
        db.commit()
        return {"message": "Ligne de commande supprimée avec succès"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Impossible de supprimer la ligne de commande")
