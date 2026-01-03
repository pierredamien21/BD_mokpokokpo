from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import Utilisateur
from schema.utilisateur import UtilisateurCreate, UtilisateurRead

router = APIRouter(
    prefix="/utilisateurs",
    tags=["Utilisateurs"]
)

@router.post("/", response_model=UtilisateurRead)
def create_utilisateur(data: UtilisateurCreate, db: Session = Depends(get_db)):
    user = Utilisateur(**data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/", response_model=list[UtilisateurRead])
def get_utilisateurs(db: Session = Depends(get_db)):
    return db.query(Utilisateur).all()

@router.get("/{id_utilisateur}", response_model=UtilisateurRead)
def get_utilisateur(id_utilisateur: int, db: Session = Depends(get_db)):
    user = db.query(Utilisateur).get(id_utilisateur)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user
