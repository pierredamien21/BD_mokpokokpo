from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import Commande, Client
from schema.commande import CommandeCreate, CommandeRead
from security.access_control import RoleChecker
from schema.enums import RoleEnum
from security.dependencies import get_current_user
from models.model import Commande, Client, Utilisateur

router = APIRouter(
    prefix="/commandes",
    tags=["Commandes"]
)

@router.post("/", response_model=CommandeRead, dependencies=[Depends(RoleChecker([RoleEnum.CLIENT, RoleEnum.ADMIN]))])
def create_commande(data: CommandeCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    # Vérification : Le client de la commande doit correspondre à l'utilisateur connecté
    # Note: data.id_utilisateur ici fait référence au client.id_utilisateur (FK table client PK utilisateur)
    if current_user.role != RoleEnum.ADMIN:
        # Note: On compare l'id_utilisateur du client lié avec l'utilisateur connecté
        client = db.get(Client, data.id_client)
        if not client or client.id_utilisateur != current_user.id_utilisateur:
             raise HTTPException(status_code=403, detail="Vous ne pouvez pas passer une commande pour un autre client")

    client = db.get(Client, data.id_client)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")

    commande = Commande(**data.model_dump())
    db.add(commande)
    db.commit()
    db.refresh(commande)
    return commande

@router.get("/", response_model=list[CommandeRead], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]))])
def get_commandes(db: Session = Depends(get_db)):
    return db.query(Commande).all()

@router.get("/{id_commande}", response_model=CommandeRead)
def get_commande(id_commande: int, db: Session = Depends(get_db)):
    commande = db.get(Commande, id_commande)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return commande
