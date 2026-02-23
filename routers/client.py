from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import Client, Utilisateur
from schema.client import ClientCreate, ClientRead
from security.dependencies import get_current_user
from security.access_control import RoleChecker
from schema.enums import RoleEnum
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)

@router.post("/", response_model=ClientRead)
def create_client(data: ClientCreate, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    # Vérification : Un utilisateur ne peut créer qu'un client pour lui-même (sauf Admin)
    if current_user.role != RoleEnum.ADMIN and data.id_utilisateur != current_user.id_utilisateur:
        raise HTTPException(status_code=403, detail="Vous ne pouvez pas créer un client pour un autre utilisateur")

    utilisateur = db.get(Utilisateur, data.id_utilisateur)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur inexistant")

    if utilisateur.role != "CLIENT":
        raise HTTPException(status_code=400, detail="Le rôle utilisateur n'est pas CLIENT")

    client = Client(**data.model_dump())
    try:
        db.add(client)
        db.commit()
        db.refresh(client)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Ce client existe déjà ou erreur d'intégrité")
    return client

@router.get("/{id_client}", response_model=ClientRead)
def get_client(id_client: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    client = db.get(Client, id_client)
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Vérifier les permissions (Admin ou propriétaire)
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        if client.id_utilisateur != current_user.id_utilisateur:
            raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    return client

@router.delete("/{id_client}")
def delete_client(id_client: int, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    
    client = db.get(Client, id_client)
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    if not client.actif:
        raise HTTPException(status_code=400, detail="Client déjà désactivé")
    
    # Soft delete: désactivation au lieu de suppression physique
    client.actif = False
    db.commit()
    return {"message": "Client désactivé avec succès"}

@router.get("/", response_model=list[ClientRead])
def get_clients(db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]:
        raise HTTPException(status_code=403, detail="Permissions insuffisantes")
    # Filtrer uniquement les clients actifs
    return db.query(Client).filter(Client.actif == True).all()
