from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.model import Client, Utilisateur
from schema.client import ClientCreate, ClientRead

router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)

@router.post("/", response_model=ClientRead)
def create_client(data: ClientCreate, db: Session = Depends(get_db)):
    utilisateur = db.query(Utilisateur).get(data.id_utilisateur)
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur inexistant")

    if utilisateur.role != "CLIENT":
        raise HTTPException(status_code=400, detail="Le rôle utilisateur n'est pas CLIENT")

    client = Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client

@router.get("/", response_model=list[ClientRead])
def get_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()
