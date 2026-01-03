from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import Utilisateur
from schema.utilisateur import UtilisateurCreate, UtilisateurRead
from security.hashing import hash_password
from security.dependencies import get_current_user, get_current_user_optional
from security.access_control import RoleChecker
from schema.enums import RoleEnum
from schema.enums import RoleEnum
from sqlalchemy.exc import IntegrityError
from main import limiter
from fastapi import Request

router = APIRouter(
    prefix="/utilisateurs",
    tags=["Utilisateurs"]
)

@router.post("/", response_model=UtilisateurRead)
@limiter.limit("10/minute")
def create_utilisateur(
    data: UtilisateurCreate, 
    request: Request, 
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user_optional)
):
    # Restriction création rôles élevés
    if data.role != RoleEnum.CLIENT:
        if not current_user or current_user.role != RoleEnum.ADMIN:
            raise HTTPException(
                status_code=403, 
                detail="Seuls les administrateurs peuvent créer des employés (Gestionnaires, Admins)"
            )
    # Hachage du mot de passe
    hashed_pwd = hash_password(data.mot_de_passe)
    
    # Création de l'utilisateur avec le mot de passe haché
    user_data = data.model_dump()
    user_data.pop("mot_de_passe")  # On retire le mot de passe en clair
    
    user = Utilisateur(**user_data, mot_de_passe=hashed_pwd)
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        
    return user

@router.get("/", response_model=list[UtilisateurRead], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))])
def get_utilisateurs(db: Session = Depends(get_db)):
    return db.query(Utilisateur).all()

@router.get("/{id_utilisateur}", response_model=UtilisateurRead)
def get_utilisateur(id_utilisateur: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    # Confidentialité : Seul l'admin ou le propriétaire peut voir le profil
    if current_user.role != RoleEnum.ADMIN and current_user.id_utilisateur != id_utilisateur:
        raise HTTPException(
            status_code=403,
            detail="Vous n'êtes pas autorisé à consulter ce profil"
        )

    user = db.get(Utilisateur, id_utilisateur)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user
