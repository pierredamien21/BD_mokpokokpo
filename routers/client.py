from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.model import Client
from schema.client import ClientCreate, ClientOut

router = APIRouter(prefix="/clients", tags=["Clients"])

@router.post("/", response_model=ClientOut)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    db_client = Client(**client.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.get("/", response_model=list[ClientOut])
def get_clients(db: Session = Depends(get_db)):
    return db.query(Client).all()
