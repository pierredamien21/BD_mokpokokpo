from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.model import Reservation, Client
from schema.reservation import ReservationCreate, ReservationRead

from security.access_control import RoleChecker
from schema.enums import RoleEnum

router = APIRouter(
    prefix="/reservations",
    tags=["Réservations"]
)

@router.post("/", response_model=ReservationRead, dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.CLIENT]))])
def create_reservation(data: ReservationCreate, db: Session = Depends(get_db)):
    if not db.get(Client, data.id_utilisateur):
        raise HTTPException(status_code=404, detail="Client introuvable")

    reservation = Reservation(**data.model_dump())
    try:
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erreur lors de la création de la réservation")
    return reservation

@router.get("/", response_model=list[ReservationRead], dependencies=[Depends(RoleChecker([RoleEnum.ADMIN, RoleEnum.GEST_COMMERCIAL]))])
def get_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).all()

@router.get("/{id_reservation}", response_model=ReservationRead)
def get_reservation(id_reservation: int, db: Session = Depends(get_db)):
    reservation = db.get(Reservation, id_reservation)
    if not reservation:
        raise HTTPException(status_code=404, detail="Réservation introuvable")
    return reservation
