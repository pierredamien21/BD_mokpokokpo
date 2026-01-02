from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.model import Reservation
from schema.reservation import ReservationCreate, ReservationOut

router = APIRouter(prefix="/reservations", tags=["Reservations"])

@router.post("/", response_model=ReservationOut)
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    db_reservation = Reservation(**reservation.model_dump())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

@router.get("/", response_model=list[ReservationOut])
def get_reservations(db: Session = Depends(get_db)):
    return db.query(Reservation).all()