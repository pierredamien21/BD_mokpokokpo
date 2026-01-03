from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models.model import Reservation
from schema.reservation import ReservationCreate, ReservationRead

router = APIRouter(
    prefix="/reservations",
    tags=["Réservations"]
)

@router.post("/", response_model=ReservationRead)
def create_reservation(data: ReservationCreate, db: Session = Depends(get_db)):
    reservation = Reservation(**data.model_dump())
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation
