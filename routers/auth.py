from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database import get_db
from models.model import Utilisateur
from schema.utilisateur import LoginRequest, TokenResponse
from security.hashing import verify_password
from security.jwt import create_access_token
from main import limiter
from fastapi import Request

router = APIRouter(
    prefix="/auth",
    tags=["Authentification"]
)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(
        Utilisateur.email == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.mot_de_passe
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants incorrects"
        )

    token = create_access_token({
        "sub": str(user.id_utilisateur),
        "role": user.role
    })

    return {"access_token": token}
